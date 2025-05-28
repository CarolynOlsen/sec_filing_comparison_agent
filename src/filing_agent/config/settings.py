"""Application settings and configuration."""

import os
from typing import Optional
from pydantic import Field

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # SEC EDGAR Configuration
    sec_user_agent: str = Field(
        default="filing-agent contact@example.com",
        description="User agent for SEC requests (required by SEC)"
    )
    sec_api_base_url: str = Field(
        default="https://data.sec.gov",
        description="SEC EDGAR API base URL"
    )
    edgar_request_delay: float = Field(
        default=0.1,
        description="Delay between SEC requests in seconds"
    )
    
    # Application Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    cache_dir: str = Field(default="./data/cache", description="Cache directory")
    filings_dir: str = Field(default="./data/filings", description="Filings storage directory")
    
    # MCP Server Configuration
    mcp_server_host: str = Field(default="localhost", description="MCP server host")
    mcp_server_port: int = Field(default=8000, description="MCP server port")
    
    # Anthropic API Configuration (optional for future use)
    anthropic_api_key: Optional[str] = Field(None, description="Anthropic API key")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings() 