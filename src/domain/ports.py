from abc import ABC, abstractmethod
from .models import BatchResponse, FoldersResponse
from typing import List, Any

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
