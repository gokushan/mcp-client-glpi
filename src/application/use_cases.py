from src.domain.ports import ContractServicePort
from src.domain.models import BatchResponse, FoldersResponse
from typing import List, Any

class ProcessContractsUseCase:
    def __init__(self, contract_service: ContractServicePort):
        self.contract_service = contract_service

    async def execute(self) -> BatchResponse:
        """Execute the batch contract processing use case."""
        return await self.contract_service.process_batch_contracts()

class ListToolsUseCase:
    def __init__(self, contract_service: ContractServicePort):
        self.contract_service = contract_service

    async def execute(self) -> List[Any]:
        """Execute the list tools use case."""
        return await self.contract_service.list_tools()

class InitializeMCPUseCase:
    def __init__(self, contract_service: ContractServicePort):
        self.contract_service = contract_service

    async def execute(self) -> None:
        """Execute the MCP initialization use case."""
        await self.contract_service.initialize()

class GetFoldersInfoUseCase:
    def __init__(self, contract_service: ContractServicePort):
        self.contract_service = contract_service

    async def execute(self) -> FoldersResponse:
        """Execute the get folders information use case."""
        return await self.contract_service.get_folders_info()
