import asyncio
import logging
from typing import Awaitable, Callable, Optional

from src.application.use_cases import ProcessContractsUseCase
from src.domain.gmail_models import (
    GmailBatchResult,
    GmailBatchStage,
)
from src.domain.ports import GmailServicePort
from src.infrastructure.adapters.mcp.gmail_client import GmailRemoteError

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[GmailBatchResult], Awaitable[None]]


class GmailBatchOrchestratorUseCase:
    """Orchestrates: fetch unread email → trigger GLPI batch processing → mark as read.

    Serialized via a shared asyncio.Lock: if a run is already in progress,
    returns immediately with stage=busy (the UI disables the button while busy).
    Mark-as-read is always attempted when there is an email, even on partial errors.
    """

    def __init__(
        self,
        gmail_service: GmailServicePort,
        process_contracts: ProcessContractsUseCase,
        lock: Optional[asyncio.Lock] = None,
        dest_folder: Optional[str] = None,
    ):
        self._gmail = gmail_service
        self._process = process_contracts
        self._lock = lock or asyncio.Lock()
        self._dest_folder = dest_folder

    @property
    def lock(self) -> asyncio.Lock:
        return self._lock

    async def execute(
        self, progress_cb: Optional[ProgressCallback] = None
    ) -> GmailBatchResult:
        async def emit(result: GmailBatchResult) -> None:
            if progress_cb is not None:
                try:
                    await progress_cb(result)
                except Exception:
                    logger.exception("progress_cb raised; ignoring")

        if self._lock.locked():
            busy = GmailBatchResult(
                stage=GmailBatchStage.BUSY,
                error="Ya hay un batch Gmail en ejecución",
            )
            await emit(busy)
            return busy

        async with self._lock:
            return await self._run(emit)

    async def _run(self, emit: Callable[[GmailBatchResult], Awaitable[None]]) -> GmailBatchResult:
        await emit(GmailBatchResult(stage=GmailBatchStage.ANALYZING_GMAIL))

        try:
            fetch = await self._gmail.fetch_latest_unread(self._dest_folder)
        except GmailRemoteError as exc:
            result = GmailBatchResult(
                stage=GmailBatchStage.ERROR,
                error=exc.message,
                error_code=exc.code,
            )
            await emit(result)
            return result
        except Exception as exc:
            logger.exception("fetch_latest_unread failed")
            result = GmailBatchResult(
                stage=GmailBatchStage.ERROR,
                error=str(exc),
                error_code="fetch_failed",
            )
            await emit(result)
            return result

        if fetch.email is None:
            result = GmailBatchResult(
                stage=GmailBatchStage.DONE,
                attachments_downloaded=0,
                attachments_rejected=fetch.attachments_rejected_count,
            )
            await emit(result)
            return result

        email = fetch.email
        downloaded = len(fetch.attachments_downloaded)
        rejected = fetch.attachments_rejected_count

        await emit(
            GmailBatchResult(
                stage=GmailBatchStage.DOWNLOADING,
                email=email,
                attachments_downloaded=downloaded,
                attachments_rejected=rejected,
            )
        )

        batch = None
        process_error: Optional[str] = None
        process_error_code: Optional[str] = None

        if downloaded > 0:
            await emit(
                GmailBatchResult(
                    stage=GmailBatchStage.PROCESSING_LLM,
                    email=email,
                    attachments_downloaded=downloaded,
                    attachments_rejected=rejected,
                )
            )
            try:
                batch = await self._process.execute()
                await emit(
                    GmailBatchResult(
                        stage=GmailBatchStage.UPLOADING_GLPI,
                        email=email,
                        attachments_downloaded=downloaded,
                        attachments_rejected=rejected,
                        batch=batch,
                    )
                )
            except Exception as exc:
                logger.exception("process_batch_contracts failed")
                process_error = str(exc)
                process_error_code = "process_failed"

        marked: Optional[bool] = None
        mark_error: Optional[str] = None
        mark_error_code: Optional[str] = None
        try:
            mark = await self._gmail.mark_as_read(email.email_id)
            marked = mark.success
        except GmailRemoteError as exc:
            marked = False
            mark_error = exc.message
            mark_error_code = exc.code
        except Exception as exc:
            logger.exception("mark_as_read failed for email_id=%s", email.email_id)
            marked = False
            mark_error = str(exc)
            mark_error_code = "mark_failed"

        final_error = process_error or mark_error
        final_code = process_error_code or mark_error_code
        stage = GmailBatchStage.ERROR if final_error else GmailBatchStage.DONE

        result = GmailBatchResult(
            stage=stage,
            email=email,
            attachments_downloaded=downloaded,
            attachments_rejected=rejected,
            batch=batch,
            marked_as_read=marked,
            error=final_error,
            error_code=final_code,
        )
        await emit(result)
        return result
