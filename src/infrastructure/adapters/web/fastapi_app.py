import asyncio
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from src.application.use_cases import ProcessContractsUseCase, ListToolsUseCase, InitializeMCPUseCase, GetFoldersInfoUseCase
from src.application.gmail_orchestrator import GmailBatchOrchestratorUseCase
from src.domain.gmail_models import GmailBatchResult, GmailBatchStage
from src.infrastructure.adapters.mcp.client import MCPServerAdapter
from src.infrastructure.adapters.mcp.gmail_client import MCPGmailAdapter
from src.infrastructure.config import settings
import logging
import json
from typing import Any


_STAGE_MESSAGES: dict[GmailBatchStage, str] = {
    GmailBatchStage.ANALYZING_GMAIL: "Analizando bandeja de Gmail…",
    GmailBatchStage.DOWNLOADING: "Descargando adjuntos del correo…",
    GmailBatchStage.PROCESSING_LLM: "Procesando contratos con el modelo de lenguaje…",
    GmailBatchStage.UPLOADING_GLPI: "Subiendo resultados a GLPI…",
    GmailBatchStage.DONE: "Proceso completado",
    GmailBatchStage.ERROR: "Se produjo un error durante el proceso",
    GmailBatchStage.BUSY: "Ya hay un procesamiento en curso",
}


def _gmail_stage_message(result: GmailBatchResult) -> str:
    base = _STAGE_MESSAGES.get(result.stage, result.stage.value)
    if result.stage == GmailBatchStage.ERROR and result.error:
        return f"{base}: {result.error}"
    if result.stage == GmailBatchStage.DONE and result.email is None:
        return "No hay correos nuevos pendientes"
    return base

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

mcp_gmail_adapter = MCPGmailAdapter()
gmail_batch_lock = asyncio.Lock()
gmail_orchestrator_use_case = GmailBatchOrchestratorUseCase(
    gmail_service=mcp_gmail_adapter,
    process_contracts=process_use_case,
    lock=gmail_batch_lock,
    dest_folder=settings.gmail_dest_folder,
)

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

_STATIC_DIR = Path(__file__).parent / "static"


@app.get("/mcpserver", include_in_schema=False)
@app.get("/mcpserver/", include_in_schema=False)
async def mcpserver_ui():
    """Serve the Gmail batch UI (Alpine + Tailwind via CDN)."""
    html = (_STATIC_DIR / "gmailserver.html").read_text(encoding="utf-8")
    html = html.replace("__GLPI_WEB_URL__", settings.glpi_web_url.rstrip("/"))
    return HTMLResponse(html)


@app.post("/gmail-batch", response_class=PrettyJSONResponse)
async def gmail_batch():
    """Trigger the Gmail → GLPI orchestrated batch. Returns the final result."""
    try:
        logger.info("Received request to /gmail-batch")
        result = await gmail_orchestrator_use_case.execute()
        if result.stage == GmailBatchStage.BUSY:
            return PrettyJSONResponse(
                status_code=409,
                content=result.model_dump(mode="json", exclude_none=True),
            )
        return result
    except Exception as e:
        logger.error(f"Error in /gmail-batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/gmail-batch/stream")
async def gmail_batch_stream():
    """Stream Gmail batch progress as Server-Sent Events."""
    logger.info("Received request to /gmail-batch/stream")
    queue: asyncio.Queue = asyncio.Queue()
    sentinel = object()

    async def progress_cb(result: GmailBatchResult) -> None:
        await queue.put(result)

    async def runner() -> None:
        try:
            await gmail_orchestrator_use_case.execute(progress_cb=progress_cb)
        except Exception as exc:
            logger.exception("gmail-batch stream runner failed")
            await queue.put(
                GmailBatchResult(
                    stage=GmailBatchStage.ERROR,
                    error=str(exc),
                    error_code="stream_runner_failed",
                )
            )
        finally:
            await queue.put(sentinel)

    task = asyncio.create_task(runner())

    async def event_stream():
        try:
            while True:
                item = await queue.get()
                if item is sentinel:
                    break
                payload = {
                    "stage": item.stage.value,
                    "message": _gmail_stage_message(item),
                    "data": item.model_dump(mode="json", exclude_none=True),
                }
                yield (
                    f"event: progress\n"
                    f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
                )
        finally:
            if not task.done():
                task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


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
