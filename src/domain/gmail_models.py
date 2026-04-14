from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from src.domain.models import BatchResponse


class GmailAttachment(BaseModel):
    filename: str
    mime_type: str
    size_bytes: int
    saved_path: Optional[str] = None


class GmailEmail(BaseModel):
    email_id: str
    thread_id: str
    subject: str = ""
    sender: str = ""
    received_at: Optional[str] = None


class FetchUnreadResult(BaseModel):
    email: Optional[GmailEmail] = None
    attachments_downloaded: List[GmailAttachment] = []
    attachments_rejected_count: int = 0


class MarkReadResult(BaseModel):
    email_id: str
    success: bool


class GmailBatchStage(str, Enum):
    ANALYZING_GMAIL = "analyzing_gmail"
    DOWNLOADING = "downloading"
    PROCESSING_LLM = "processing_llm"
    UPLOADING_GLPI = "uploading_glpi"
    DONE = "done"
    ERROR = "error"
    BUSY = "busy"


class GmailBatchResult(BaseModel):
    stage: GmailBatchStage
    email: Optional[GmailEmail] = None
    attachments_downloaded: int = 0
    attachments_rejected: int = 0
    batch: Optional[BatchResponse] = None
    marked_as_read: Optional[bool] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
