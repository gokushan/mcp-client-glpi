import asyncio
import unittest
from unittest.mock import AsyncMock

from src.application.gmail_orchestrator import GmailBatchOrchestratorUseCase
from src.domain.gmail_models import (
    FetchUnreadResult,
    GmailAttachment,
    GmailBatchStage,
    GmailEmail,
    MarkReadResult,
)
from src.domain.models import BatchResponse, ProcessResult
from src.infrastructure.adapters.mcp.gmail_client import GmailRemoteError


def _email() -> GmailEmail:
    return GmailEmail(email_id="m1", thread_id="t1", subject="s", sender="a@b.c")


def _fetch_with_attachments(n: int = 1) -> FetchUnreadResult:
    return FetchUnreadResult(
        email=_email(),
        attachments_downloaded=[
            GmailAttachment(filename=f"f{i}.pdf", mime_type="application/pdf", size_bytes=10)
            for i in range(n)
        ],
        attachments_rejected_count=0,
    )


def _batch_response() -> BatchResponse:
    return BatchResponse(
        results=[ProcessResult(file="f0.pdf", status="success", contract_id=1)],
        summary_text="ok",
    )


class _FakeProcess:
    def __init__(self, response=None, raises=None):
        self._response = response
        self._raises = raises
        self.called = 0

    async def execute(self):
        self.called += 1
        if self._raises is not None:
            raise self._raises
        return self._response


class TestGmailOrchestrator(unittest.IsolatedAsyncioTestCase):
    async def test_no_unread_email_returns_done(self):
        gmail = AsyncMock()
        gmail.fetch_latest_unread.return_value = FetchUnreadResult(email=None)
        process = _FakeProcess(response=_batch_response())

        uc = GmailBatchOrchestratorUseCase(gmail, process)
        result = await uc.execute()

        self.assertEqual(result.stage, GmailBatchStage.DONE)
        self.assertIsNone(result.email)
        self.assertEqual(process.called, 0)
        gmail.mark_as_read.assert_not_called()

    async def test_happy_path_processes_and_marks_as_read(self):
        gmail = AsyncMock()
        gmail.fetch_latest_unread.return_value = _fetch_with_attachments()
        gmail.mark_as_read.return_value = MarkReadResult(email_id="m1", success=True)
        process = _FakeProcess(response=_batch_response())

        stages: list[GmailBatchStage] = []

        async def cb(r):
            stages.append(r.stage)

        uc = GmailBatchOrchestratorUseCase(gmail, process)
        result = await uc.execute(progress_cb=cb)

        self.assertEqual(result.stage, GmailBatchStage.DONE)
        self.assertTrue(result.marked_as_read)
        self.assertEqual(process.called, 1)
        gmail.mark_as_read.assert_awaited_once_with("m1")
        self.assertEqual(
            stages,
            [
                GmailBatchStage.ANALYZING_GMAIL,
                GmailBatchStage.DOWNLOADING,
                GmailBatchStage.PROCESSING_LLM,
                GmailBatchStage.UPLOADING_GLPI,
                GmailBatchStage.DONE,
            ],
        )

    async def test_process_fails_still_marks_as_read(self):
        gmail = AsyncMock()
        gmail.fetch_latest_unread.return_value = _fetch_with_attachments()
        gmail.mark_as_read.return_value = MarkReadResult(email_id="m1", success=True)
        process = _FakeProcess(raises=RuntimeError("LLM timeout"))

        uc = GmailBatchOrchestratorUseCase(gmail, process)
        result = await uc.execute()

        self.assertEqual(result.stage, GmailBatchStage.ERROR)
        self.assertEqual(result.error_code, "process_failed")
        self.assertIn("LLM timeout", result.error)
        self.assertTrue(result.marked_as_read)
        gmail.mark_as_read.assert_awaited_once_with("m1")

    async def test_gmail_remote_error_on_fetch_surfaces_code(self):
        gmail = AsyncMock()
        gmail.fetch_latest_unread.side_effect = GmailRemoteError(
            code="oauth_expired", message="Re-auth needed"
        )
        process = _FakeProcess(response=_batch_response())

        uc = GmailBatchOrchestratorUseCase(gmail, process)
        result = await uc.execute()

        self.assertEqual(result.stage, GmailBatchStage.ERROR)
        self.assertEqual(result.error_code, "oauth_expired")
        gmail.mark_as_read.assert_not_called()

    async def test_email_without_allowed_attachments_skips_processing_and_marks(self):
        gmail = AsyncMock()
        gmail.fetch_latest_unread.return_value = FetchUnreadResult(
            email=_email(), attachments_downloaded=[], attachments_rejected_count=2
        )
        gmail.mark_as_read.return_value = MarkReadResult(email_id="m1", success=True)
        process = _FakeProcess(response=_batch_response())

        uc = GmailBatchOrchestratorUseCase(gmail, process)
        result = await uc.execute()

        self.assertEqual(result.stage, GmailBatchStage.DONE)
        self.assertEqual(process.called, 0)
        self.assertTrue(result.marked_as_read)
        self.assertEqual(result.attachments_rejected, 2)

    async def test_lock_busy_returns_immediately(self):
        gmail = AsyncMock()
        gmail.fetch_latest_unread.return_value = _fetch_with_attachments()
        gmail.mark_as_read.return_value = MarkReadResult(email_id="m1", success=True)
        process = _FakeProcess(response=_batch_response())

        lock = asyncio.Lock()
        uc = GmailBatchOrchestratorUseCase(gmail, process, lock=lock)

        await lock.acquire()
        try:
            result = await uc.execute()
        finally:
            lock.release()

        self.assertEqual(result.stage, GmailBatchStage.BUSY)
        self.assertEqual(process.called, 0)
        gmail.fetch_latest_unread.assert_not_called()

    async def test_mark_as_read_failure_when_process_ok_is_error_stage(self):
        gmail = AsyncMock()
        gmail.fetch_latest_unread.return_value = _fetch_with_attachments()
        gmail.mark_as_read.side_effect = GmailRemoteError(
            code="gmail_api_error", message="rate limited"
        )
        process = _FakeProcess(response=_batch_response())

        uc = GmailBatchOrchestratorUseCase(gmail, process)
        result = await uc.execute()

        self.assertEqual(result.stage, GmailBatchStage.ERROR)
        self.assertEqual(result.error_code, "gmail_api_error")
        self.assertFalse(result.marked_as_read)


if __name__ == "__main__":
    unittest.main()
