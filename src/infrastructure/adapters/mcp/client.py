from src.domain.ports import ContractServicePort
from src.domain.models import BatchResponse, ProcessResult, FoldersResponse
from src.infrastructure.config import settings
from typing import List, Any
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
import logging

logger = logging.getLogger(__name__)

class MCPServerAdapter(ContractServicePort):
    def __init__(self):
        self.server_url = settings.mcp_server_url
        self.tool_name = settings.mcp_tool_name
        self.folders_tool_name = settings.mcp_folders_tool_name

    async def initialize(self) -> None:
        """Initialize the connection to the MCP Server and verify it."""
        logger.info(f"Initializing MCP session with {self.server_url}")
        try:
            async with streamable_http_client(self.server_url) as (read_stream, write_stream, get_session_id):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    logger.info("MCP session initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MCP session: {e}")
            raise RuntimeError(f"MCP Initialization failed: {str(e)}")

    async def list_tools(self) -> List[Any]:
        """List available tools on the MCP Server."""
        logger.info(f"Listing tools from MCP Server at {self.server_url}")
        try:
            async with streamable_http_client(self.server_url) as (read_stream, write_stream, get_session_id):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    result = await session.list_tools()
                    return result.tools
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            raise RuntimeError(f"Failed to list tools: {str(e)}")

    async def process_batch_contracts(self) -> BatchResponse:
        """Call the configured MCP Server tool via HTTP."""
        logger.info(f"Connecting to MCP Server at {self.server_url} to call {self.tool_name}")
        
        try:
            async with streamable_http_client(self.server_url) as (read_stream, write_stream, get_session_id):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    
                    logger.info(f"Calling tool '{self.tool_name}'")
                    result = await session.call_tool(self.tool_name, arguments={})
                    
                    if not result.content or len(result.content) == 0:
                         raise ValueError("No content received from MCP Server")
                         
                    import json
                    raw_data = json.loads(result.content[0].text)
                    
                    return BatchResponse(
                        results=[ProcessResult(**r) for r in raw_data.get("results", [])],
                        summary_text=raw_data.get("summary_text", "No summary provided")
                    )
        except Exception as e:
            logger.error(f"Error communicating with MCP Server: {e}")
            raise RuntimeError(f"Failed to process contracts: {str(e)}")

    async def get_folders_info(self) -> FoldersResponse:
        """Call the MCP Server tool to get folder paths."""
        logger.info(f"Connecting to MCP Server at {self.server_url} to call {self.folders_tool_name}")
        
        try:
            async with streamable_http_client(self.server_url) as (read_stream, write_stream, get_session_id):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    
                    logger.info(f"Calling tool '{self.folders_tool_name}'")
                    result = await session.call_tool(self.folders_tool_name, arguments={})
                    
                    logger.info(f"Raw result from MCP tool '{self.folders_tool_name}': {result}")

                    if not result.content or len(result.content) == 0:
                         logger.error(f"No content block in result from {self.folders_tool_name}")
                         raise ValueError("No content received from MCP Server for folders")
                         
                    import json
                    try:
                        raw_data = json.loads(result.content[0].text)
                        logger.info(f"Parsed folders data: {raw_data}")
                    except (json.JSONDecodeError, AttributeError) as e:
                        logger.error(f"Failed to parse JSON from MCP tool output: {e}. Content: {result.content[0].text if result.content else 'N/A'}")
                        raise ValueError(f"Invalid JSON response from MCP Server: {str(e)}")
                    
                    # Handle both dict and list responses
                    if isinstance(raw_data, dict):
                        return FoldersResponse(**raw_data)
                    elif isinstance(raw_data, list):
                        # If it's a list, we assume they are all to_process folders
                        return FoldersResponse(
                            to_process=raw_data,
                            processed=[],
                            errors=[],
                            success=True
                        )
                    else:
                        raise ValueError(f"Unexpected data format from MCP tool: {type(raw_data)}")
        except Exception as e:
            logger.error(f"Error communicating with MCP Server for folders: {e}")
            raise RuntimeError(f"Failed to get folders info: {str(e)}")
