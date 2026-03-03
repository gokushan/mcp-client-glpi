from pydantic import BaseModel
from typing import Any, List, Optional

class ProcessResult(BaseModel):
    file: str
    processed_path: Optional[str] = None
    status: str
    contract_id: Optional[int] = None
    contract_name: Optional[str] = None
    document_attached: bool = False
    error: Optional[str] = None
    error_code: Optional[int] = None
    error_description: Optional[str] = None

class BatchResponse(BaseModel):
    results: List[ProcessResult]
    summary_text: str

class FoldersResponse(BaseModel):
    to_process: List[str]
    processed: List[str]
    errors: List[str]
    errors_details: Optional[List[dict[str, Any]]] = None
    success: bool
