from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from src.application.use_cases import ProcessContractsUseCase, ListToolsUseCase, InitializeMCPUseCase, GetFoldersInfoUseCase
from src.infrastructure.adapters.mcp.client import MCPServerAdapter
from src.infrastructure.config import settings
import logging
import json
from typing import Any

# Configure logger
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

class PrettyJSONResponse(JSONResponse):
    """Custom JSONResponse that returns indented JSON."""
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,
            separators=(", ", ": "),
        ).encode("utf-8")

app = FastAPI(title="MCP Client GLPI API")

@app.middleware("http")
async def ip_restriction_middleware(request: Request, call_next):
    """Restricts API access based on client IP addresses."""
    # Check if restriction is disabled or if IP is allowed
    allowed = settings.allowed_ips
    
    if "*" in allowed:
        return await call_next(request)
    
    client_ip = request.client.host
    
    if client_ip not in allowed:
        logger.warning(f"Access denied for unauthorized IP: {client_ip}")
        return PrettyJSONResponse(
            status_code=403,
            content={"detail": "Forbidden: IP address not authorized."}
        )
        
    return await call_next(request)

# Dependency Injection
mcp_adapter = MCPServerAdapter()
process_use_case = ProcessContractsUseCase(mcp_adapter)
list_tools_use_case = ListToolsUseCase(mcp_adapter)
init_use_case = InitializeMCPUseCase(mcp_adapter)
folders_use_case = GetFoldersInfoUseCase(mcp_adapter)

@app.on_event("startup")
async def startup_event():
    """Perform MCP initialization on startup if configured."""
    if settings.mcp_initialize_on_startup:
        try:
            logger.info("Starting MCP initialization...")
            await init_use_case.execute()
            logger.info("MCP initialization completed.")
        except Exception as e:
            logger.error(f"Failed to initialize MCP on startup: {e}")
            # We don't necessarily want to stop the app from starting, 
            # but it will be logged.

@app.post("/processcontract", response_class=PrettyJSONResponse)
async def process_contract():
    """
    Endpoint to trigger batch contract processing.
    This maps to the configured MCP tool (default: tool_batch_contracts).
    """
    try:
        logger.info(f"Received request to /processcontract (maps to {settings.mcp_tool_name})")
        result = await process_use_case.execute()
        return result
    except Exception as e:
        logger.error(f"Error in /processcontract: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools", response_class=PrettyJSONResponse)
async def list_tools():
    """Endpoint to list available tools from the MCP Server."""
    try:
        logger.info("Received request to /tools")
        tools = await list_tools_use_case.execute()
        return {"tools": tools}
    except Exception as e:
        logger.error(f"Error in /tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/folders", response_class=PrettyJSONResponse)
async def list_folders():
    """Endpoint to get specialized folders info from the MCP Server."""
    try:
        logger.info("Received request to /folders")
        return await folders_use_case.execute()
    except Exception as e:
        logger.error(f"Error in /folders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/healthcheck", response_class=PrettyJSONResponse)
async def healthcheck():
    """
    Enhanced health check that verifies connectivity with the MCP Server.
    """
    try:
        folders_info = await folders_use_case.execute()
        return {
            "status": "ok",
            "mcp_server": {
                "connected": True,
                "url": settings.mcp_server_url,
                "folders_status": {
                    "to_process_count": len(folders_info.to_process),
                    "success": folders_info.success
                }
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "mcp_server": {
                "connected": False,
                "error": str(e)
            }
        }
