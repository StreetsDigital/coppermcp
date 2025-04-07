"""Configuration management for the Copper MCP Server.

This module handles loading and validation of environment variables using Pydantic Settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Copper API Configuration
    copper_api_key: str = Field(
        ...,
        description="Copper CRM API Key for authentication",
        alias="COPPER_API_KEY"
    )
    copper_user_email: str = Field(
        ...,
        description="Copper CRM User Email for authentication",
        alias="COPPER_USER_EMAIL"
    )
    
    # Copper API Base URL
    copper_api_base_url: str = Field(
        "https://api.copper.com/developer_api/v1",
        description="Base URL for Copper API",
        alias="COPPER_API_BASE_URL"
    )
    
    # Optional: Configure environment file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Create global settings instance
settings = Settings() 