from abc import ABC, abstractmethod
from .models import BatchResponse, FoldersResponse
from .gmail_models import FetchUnreadResult, MarkReadResult
from typing import List, Any, Optional

class ContractServicePort(ABC):
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the connection to the MCP Server."""
        pass

    @abstractmethod
    async def list_tools(self) -> List[Any]:
        """List available tools on the MCP Server."""
        pass

    @abstractmethod
    async def process_batch_contracts(self) -> BatchResponse:
        """Port to process batch contracts from the MCP Server."""
        pass

    @abstractmethod
    async def get_folders_info(self) -> FoldersResponse:
        """Port to get folder information from the MCP Server."""
        pass


class GmailServicePort(ABC):
    @abstractmethod
    async def fetch_latest_unread(self, dest_folder: Optional[str] = None) -> FetchUnreadResult:
        """Fetch oldest unread email and download allowed attachments. Does not mark as read."""
        pass

    @abstractmethod
    async def mark_as_read(self, email_id: str) -> MarkReadResult:
        """Remove the UNREAD label from a specific email."""
        pass
