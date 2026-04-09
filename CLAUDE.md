# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**mcp-client** is a FastAPI-based REST API that acts as an orchestrator/proxy between HTTP clients and the GLPI MCP Server. It does NOT perform processing directly; it delegates all heavy operations (LLM usage, GLPI access, file operations) to `mcp-server` via the Model Context Protocol (MCP) over Streamable HTTP transport.

**Architecture:** Hexagonal (Ports & Adapters) with three isolated layers:
- **Domain** (`src/domain/`): Pure business models & abstract ports (interfaces)
- **Application** (`src/application/`): Use cases that orchestrate workflows
- **Infrastructure** (`src/infrastructure/`): Concrete adapters (FastAPI web + MCP client)

## Development Setup

```bash
# Create virtual environment and install
python3 -m venv .venv
.venv/bin/pip install -e .

# Run development server
.venv/bin/uvicorn src.infrastructure.adapters.web.fastapi_app:app --reload

# Configure environment
cp .env.example .env
# Edit .env with MCP_SERVER_URL and ALLOWED_IPS
```

## Common Commands

```bash
# Development server (auto-reload)
.venv/bin/uvicorn src.infrastructure.adapters.web.fastapi_app:app --reload

# Run tests
pytest tests/ -v

# Code quality
black src/
ruff check src/

# Health check
curl http://localhost:8000/healthcheck

# List available tools on mcp-server
curl http://localhost:8000/tools

# Process contracts (trigger batch operation on mcp-server)
curl -X POST http://localhost:8000/processcontract
```

## Key Concepts

### Request Flow
1. HTTP request arrives at FastAPI endpoint → `ip_restriction_middleware` validates IP
2. Endpoint instantiates a **Use Case** with injected **MCP Adapter**
3. Use Case calls methods on the **ContractServicePort** (abstract interface)
4. **MCPServerAdapter** translates request to MCP protocol:
   - Opens streamable HTTP client to `MCP_SERVER_URL`
   - Initializes MCP session (handshake)
   - Calls tool on remote server
   - Deserializes JSON response
5. FastAPI returns **PrettyJSONResponse** (indented, `ensure_ascii=False`)

### Dependency Injection
- Use Cases receive dependencies in constructor, not at runtime
- All adapters and use cases are instantiated once at app startup (singleton pattern)
- This is intentional: no state is maintained between requests

### Error Codes (from mcp-server)
These codes are standardized at the server and propagated unchanged:
- **100**: Malformed/unreadable file
- **101**: Prompt injection detected
- **102**: File extension not allowed
- **103**: Path access denied / path traversal attempt
- **104**: Path/file doesn't exist
- **105**: LLM timeout or MCP session cancelled

## Critical Files

| File | Purpose |
|------|---------|
| `src/infrastructure/adapters/mcp/client.py` | **MCPServerAdapter**: implements ContractServicePort using streamable HTTP |
| `src/infrastructure/adapters/web/fastapi_app.py` | **FastAPI app**: endpoints, middleware, startup hook |
| `src/domain/models.py` | **ProcessResult**, **BatchResponse**, **FoldersResponse** (Pydantic models) |
| `src/domain/ports.py` | **ContractServicePort**: abstract interface defining what the system can do |
| `src/application/use_cases.py` | 4 use cases: ProcessContracts, ListTools, Initialize, GetFoldersInfo |
| `src/infrastructure/config.py` | Pydantic Settings with .env variables |

## Configuration

Key `.env` variables:
- `MCP_SERVER_URL`: URL of mcp-server (default: `http://localhost:8081/mcp`)
- `MCP_TOOL_NAME`: which MCP tool to call for processing (default: `tool_batch_contracts`)
- `MCP_FOLDERS_TOOL_NAME`: which MCP tool to call for folder info (default: `list_folders`)
- `MCP_INITIALIZE_ON_STARTUP`: run healthcheck on startup (default: `True`)
- `APP_HOST`, `APP_PORT`: where to listen (default: `0.0.0.0:8000`)
- `ALLOWED_IPS`: JSON list of allowed client IPs (default: `["*"]`)

## Design Principles

### Dependency Inversion
- Use Cases depend on `ContractServicePort` (abstract), not `MCPServerAdapter` (concrete)
- This allows swapping transports (HTTP → stdio, SSE, etc.) without touching business logic

### Single Responsibility
- `domain/` defines WHAT the system can do (models + interfaces)
- `application/` defines HOW to orchestrate operations (use cases)
- `infrastructure/` handles technical details (HTTP, MCP protocol, config)

### No State Between Requests
- Each HTTP request opens its own MCP session and closes it
- No connection pooling or caching between requests
- This design is intentional for simplicity

## Testing Strategy

Tests should:
- Mock the `ContractServicePort` to test use cases in isolation
- Test adapters with actual network calls (or fixtures simulating mcp-server responses)
- Verify that models serialize/deserialize correctly for FastAPI

## When Modifying...

**Adding a new endpoint?**
1. Add use case to `application/use_cases.py` (or reuse existing)
2. Add port method to `domain/ports.py` if needed
3. Implement in `MCPServerAdapter` (call the corresponding MCP tool)
4. Register endpoint in `fastapi_app.py`

**Changing the MCP communication?**
- Only modify `src/infrastructure/adapters/mcp/client.py`
- The rest of the codebase (domain, application) stays untouched

**Adding a new configuration option?**
- Add field to `Settings` class in `config.py`
- Reference in `.env.example`

## Related Projects

- **mcp-server** (sibling project): The actual processing engine. Contains all business logic for LLM processing, GLPI API integration, and file operations. This client is just a REST → MCP translator.

## Documentation

- `ARCHITECTURE.md`: Detailed breakdown of hexagonal architecture
- `FEATURES.md`: Endpoint reference with curl examples
- `DEPLOYMENT.md`: Docker and production setup
- `agents.md`: Context for AI agents working with this codebase
