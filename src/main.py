import uvicorn
from .infrastructure.adapters.web.fastapi_app import app
from .infrastructure.config import settings

def main():
    """Main entry point for the MCP Client."""
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=settings.app_port
    )

if __name__ == "__main__":
    main()
