from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mcp_server_url: str = "http://localhost:8081/mcp"
    mcp_tool_name: str = "tool_batch_contracts"
    mcp_folders_tool_name: str = "list_folders"
    mcp_initialize_on_startup: bool = True
    mcp_gmail_url: str = "http://localhost:8082/mcp"
    mcp_gmail_fetch_tool: str = "fetch_latest_unread"
    mcp_gmail_mark_tool: str = "mark_as_read"
    gmail_dest_folder: str | None = None
    glpi_web_url: str = ""
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    # Comma-separated or list of allowed IPs. Default "*" allow all for backward compatibility or ease.
    allowed_ips: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
