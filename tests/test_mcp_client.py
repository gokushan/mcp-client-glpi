import asyncio
import unittest
from unittest.mock import AsyncMock, patch
from src.infrastructure.adapters.mcp.client import MCPServerAdapter
from src.domain.models import BatchResponse

class TestMCPServerAdapter(unittest.IsolatedAsyncioTestCase):
    @patch("src.infrastructure.adapters.mcp.client.streamable_http_client")
    @patch("src.infrastructure.adapters.mcp.client.ClientSession")
    async def test_initialize(self, mock_session_cls, mock_stream_client):
        # Setup
        mock_session = AsyncMock()
        mock_session_cls.return_value.__aenter__.return_value = mock_session
        mock_stream_client.return_value.__aenter__.return_value = (AsyncMock(), AsyncMock(), AsyncMock())
        
        adapter = MCPServerAdapter()
        
        # Execute
        await adapter.initialize()
        
        # Verify
        mock_session.initialize.assert_awaited_once()

    @patch("src.infrastructure.adapters.mcp.client.streamable_http_client")
    @patch("src.infrastructure.adapters.mcp.client.ClientSession")
    async def test_list_tools(self, mock_session_cls, mock_stream_client):
        # Setup
        mock_session = AsyncMock()
        mock_list_result = AsyncMock()
        mock_list_result.tools = ["tool1", "tool2"]
        mock_session.list_tools.return_value = mock_list_result
        mock_session_cls.return_value.__aenter__.return_value = mock_session
        mock_stream_client.return_value.__aenter__.return_value = (AsyncMock(), AsyncMock(), AsyncMock())
        
        adapter = MCPServerAdapter()
        
        # Execute
        tools = await adapter.list_tools()
        
        # Verify
        self.assertEqual(tools, ["tool1", "tool2"])
        mock_session.initialize.assert_awaited_once()
        mock_session.list_tools.assert_awaited_once()

if __name__ == "__main__":
    unittest.main()
