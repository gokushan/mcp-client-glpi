import asyncio
import json
import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from src.domain.gmail_models import (
    FetchUnreadResult,
    GmailAttachment,
    GmailBatchStage,
    GmailEmail,
    MarkReadResult,
)
from src.domain.models import BatchResponse, ProcessResult
from src.infrastructure.adapters.web import fastapi_app as web


def _fetch_with_pdf() -> FetchUnreadResult:
    return FetchUnreadResult(
        email=GmailEmail(email_id="m1", thread_id="t1", subject="s", sender="a@b.c"),
        attachments_downloaded=[
            GmailAttachment(filename="c.pdf", mime_type="application/pdf", size_bytes=10)
        ],
        attachments_rejected_count=0,
    )


def _batch() -> BatchResponse:
    return BatchResponse(
        results=[ProcessResult(file="c.pdf", status="success", contract_id=42)],
        summary_text="ok",
    )


class TestGmailBatchEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(web.app)

        # Allow TestClient's fake IP through the restriction middleware.
        self._original_allowed = web.settings.allowed_ips
        web.settings.allowed_ips = ["*"]

        # Replace the singleton orchestrator's collaborators with mocks.
        self.gmail_mock = AsyncMock()
        self.gmail_mock.fetch_latest_unread.return_value = _fetch_with_pdf()
        self.gmail_mock.mark_as_read.return_value = MarkReadResult(email_id="m1", success=True)

        self.process_patcher = patch.object(
            web.gmail_orchestrator_use_case, "_gmail", self.gmail_mock
        )
        self.process_patcher.start()

        self.process_execute_patcher = patch.object(
            web.process_use_case, "execute", AsyncMock(return_value=_batch())
        )
        self.process_execute_patcher.start()

    def tearDown(self):
        self.process_patcher.stop()
        self.process_execute_patcher.stop()
        web.settings.allowed_ips = self._original_allowed

    def test_post_gmail_batch_returns_final_result(self):
        response = self.client.post("/gmail-batch")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["stage"], GmailBatchStage.DONE.value)
        self.assertEqual(body["email"]["email_id"], "m1")
        self.assertTrue(body["marked_as_read"])
        self.assertEqual(body["batch"]["results"][0]["contract_id"], 42)

    def test_post_gmail_batch_returns_409_when_busy(self):
        async def hold_lock():
            async with web.gmail_batch_lock:
                await asyncio.sleep(0.2)

        loop = asyncio.new_event_loop()
        try:
            holder = loop.create_task(hold_lock())
            # Give the holder task a tick to actually acquire the lock.
            loop.run_until_complete(asyncio.sleep(0.01))

            response = self.client.post("/gmail-batch")
            self.assertEqual(response.status_code, 409)
            self.assertEqual(response.json()["stage"], GmailBatchStage.BUSY.value)

            loop.run_until_complete(holder)
        finally:
            loop.close()

    def test_get_gmail_batch_stream_emits_sse_events(self):
        with self.client.stream("GET", "/gmail-batch/stream") as response:
            self.assertEqual(response.status_code, 200)
            self.assertIn("text/event-stream", response.headers["content-type"])
            events = []
            buffer = ""
            for chunk in response.iter_text():
                buffer += chunk
                while "\n\n" in buffer:
                    raw, buffer = buffer.split("\n\n", 1)
                    data_lines = [
                        line[len("data: "):]
                        for line in raw.splitlines()
                        if line.startswith("data: ")
                    ]
                    if data_lines:
                        events.append(json.loads("\n".join(data_lines)))

        stages = [e["stage"] for e in events]
        self.assertEqual(
            stages,
            [
                GmailBatchStage.ANALYZING_GMAIL.value,
                GmailBatchStage.DOWNLOADING.value,
                GmailBatchStage.PROCESSING_LLM.value,
                GmailBatchStage.UPLOADING_GLPI.value,
                GmailBatchStage.DONE.value,
            ],
        )
        # Spanish message is present
        self.assertTrue(all(e.get("message") for e in events))
        self.assertIn("Analizando", events[0]["message"])


if __name__ == "__main__":
    unittest.main()
