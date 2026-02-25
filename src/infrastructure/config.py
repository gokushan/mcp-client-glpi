from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mcp_server_url: str = "http://localhost:8081/mcp"
    mcp_tool_name: str = "tool_batch_contracts"
    mcp_folders_tool_name: str = "list_folders"
    mcp_initialize_on_startup: bool = True
    app_port: int = 8000
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
