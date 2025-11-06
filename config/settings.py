"""Configurações centralizadas da aplicação usando Pydantic Settings."""

import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação carregadas de variáveis de ambiente."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1", alias="OPENAI_BASE_URL"
    )

    # Anthropic
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_base_url: str = Field(
        default="https://api.anthropic.com", alias="ANTHROPIC_BASE_URL"
    )

    # Meta
    meta_api_key: Optional[str] = Field(default=None, alias="META_API_KEY")
    meta_base_url: str = Field(
        default="https://api.meta.ai/v1", alias="META_BASE_URL"
    )

    # Ollama
    ollama_base_url: str = Field(
        default="http://localhost:11434", alias="OLLAMA_BASE_URL"
    )

    # AWS
    aws_access_key_id: Optional[str] = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(
        default=None, alias="AWS_SECRET_ACCESS_KEY"
    )
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    aws_bedrock_endpoint_url: Optional[str] = Field(
        default=None, alias="AWS_BEDROCK_ENDPOINT_URL"
    )

    # Azure Storage
    azure_storage_connection_string: Optional[str] = Field(
        default=None, alias="AZURE_STORAGE_CONNECTION_STRING"
    )
    azure_storage_container_name: Optional[str] = Field(
        default=None, alias="AZURE_STORAGE_CONTAINER_NAME"
    )

    # S3
    s3_bucket_name: Optional[str] = Field(default=None, alias="S3_BUCKET_NAME")

    # Application
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    max_file_size_mb: int = Field(default=50, alias="MAX_FILE_SIZE_MB")
    cache_enabled: bool = Field(default=True, alias="CACHE_ENABLED")

    # Paths
    default_upload_path: str = Field(default="./uploads", alias="DEFAULT_UPLOAD_PATH")
    default_output_path: str = Field(default="./outputs", alias="DEFAULT_OUTPUT_PATH")


@lru_cache()
def get_settings() -> Settings:
    """Retorna uma instância singleton das configurações."""
    return Settings()

