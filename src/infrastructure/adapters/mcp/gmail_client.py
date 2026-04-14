import json
import logging
from typing import Any, Optional

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from src.domain.gmail_models import FetchUnreadResult, MarkReadResult
from src.domain.ports import GmailServicePort
from src.infrastructure.config import settings

logger = logging.getLogger(__name__)


class GmailRemoteError(RuntimeError):
    """Raised when mcp-gmail returns a typed `{error: {code, message}}` payload."""

    def __init__(self, code: str, message: str):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


class MCPGmailAdapter(GmailServicePort):
    def __init__(self):
        self.server_url = settings.mcp_gmail_url
        self.fetch_tool = settings.mcp_gmail_fetch_tool
        self.mark_tool = settings.mcp_gmail_mark_tool

    async def _call_tool(self, tool_name: str, arguments: dict) -> dict:
        logger.info("Calling mcp-gmail tool '%s' at %s", tool_name, self.server_url)
        async with streamable_http_client(self.server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)
                if not result.content:
                    raise ValueError(f"No content received from mcp-gmail tool '{tool_name}'")
                raw = json.loads(result.content[0].text)
                if not isinstance(raw, dict):
                    raise ValueError(f"Unexpected response shape from '{tool_name}': {type(raw)}")
                return raw

    @staticmethod
    def _raise_if_error(payload: dict) -> None:
        err = payload.get("error")
        if err:
            raise GmailRemoteError(
                code=err.get("code", "unknown"),
                message=err.get("message", "Unknown mcp-gmail error"),
            )

    async def fetch_latest_unread(self, dest_folder: Optional[str] = None) -> FetchUnreadResult:
        args: dict[str, Any] = {}
        if dest_folder is not None:
            args["dest_folder"] = dest_folder
        raw = await self._call_tool(self.fetch_tool, args)
        self._raise_if_error(raw)
        return FetchUnreadResult.model_validate(raw)

    async def mark_as_read(self, email_id: str) -> MarkReadResult:
        raw = await self._call_tool(self.mark_tool, {"email_id": email_id})
        self._raise_if_error(raw)
        return MarkReadResult.model_validate(raw)
