"""Configurações centralizadas da aplicação usando Streamlit Secrets ou variáveis de ambiente."""

import os
from functools import lru_cache
from typing import Optional

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


def _get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Obtém um valor de configuração de st.secrets ou variável de ambiente.
    
    Prioridade:
    1. st.secrets (se disponível) - suporta formato aninhado e plano
    2. Variável de ambiente
    3. Valor padrão
    
    Suporta dois formatos de secrets:
    - Formato plano: st.secrets["OPENAI_API_KEY"]
    - Formato aninhado: st.secrets["openai"]["api_key"]
    
    Args:
        key: Nome da chave de configuração (ex: "OPENAI_API_KEY" ou "openai_api_key")
        default: Valor padrão se não encontrado
        
    Returns:
        Valor da configuração ou None
    """
    # Tenta obter de st.secrets primeiro
    if STREAMLIT_AVAILABLE:
        try:
            if hasattr(st, "secrets") and st.secrets:
                # 1. Tenta acesso direto com a chave original (formato plano)
                if key in st.secrets:
                    value = st.secrets[key]
                    if value and str(value).strip() != "":
                        return str(value)
                
                # 2. Tenta acesso direto com chave em minúsculas
                key_lower = key.lower()
                if key_lower in st.secrets:
                    value = st.secrets[key_lower]
                    if value and str(value).strip() != "":
                        return str(value)
                
                # 3. Tenta acesso aninhado (ex: openai.api_key)
                # Converte OPENAI_API_KEY -> openai.api_key
                parts = key_lower.split("_")
                if len(parts) >= 2:
                    section = parts[0]
                    subkey = "_".join(parts[1:])
                    
                    # Tenta st.secrets["openai"]["api_key"]
                    if section in st.secrets:
                        section_dict = st.secrets[section]
                        if isinstance(section_dict, dict):
                            if subkey in section_dict:
                                value = section_dict[subkey]
                                if value and str(value).strip() != "":
                                    return str(value)
                            
                            # Tenta com subkey em formato snake_case -> camelCase
                            # ex: api_key -> apiKey
                            subkey_camel = subkey.replace("_", "")
                            if subkey_camel in section_dict:
                                value = section_dict[subkey_camel]
                                if value and str(value).strip() != "":
                                    return str(value)
        except (KeyError, AttributeError, TypeError, RuntimeError):
            # RuntimeError pode ocorrer se st.secrets não estiver disponível no contexto
            pass
    
    # Fallback para variável de ambiente
    env_value = os.getenv(key)
    if env_value:
        return env_value
    
    # Tenta também com chave em minúsculas
    env_value = os.getenv(key.lower())
    if env_value:
        return env_value
    
    return default


class Settings:
    """Configurações da aplicação carregadas de st.secrets ou variáveis de ambiente."""

    def __init__(self):
        """Inicializa as configurações."""
        # OpenAI
        self.openai_api_key = _get_secret("OPENAI_API_KEY")
        self.openai_base_url = _get_secret("OPENAI_BASE_URL", "https://api.openai.com/v1")

        # Anthropic
        self.anthropic_api_key = _get_secret("ANTHROPIC_API_KEY")
        self.anthropic_base_url = _get_secret("ANTHROPIC_BASE_URL", "https://api.anthropic.com")

        # Meta
        self.meta_api_key = _get_secret("META_API_KEY")
        self.meta_base_url = _get_secret("META_BASE_URL", "https://api.meta.ai/v1")

        # Ollama
        self.ollama_base_url = _get_secret("OLLAMA_BASE_URL", "http://localhost:11434")

        # AWS
        self.aws_access_key_id = _get_secret("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = _get_secret("AWS_SECRET_ACCESS_KEY")
        self.aws_region = _get_secret("AWS_REGION", "us-east-1")
        self.aws_bedrock_endpoint_url = _get_secret("AWS_BEDROCK_ENDPOINT_URL")

        # Azure Storage
        self.azure_storage_connection_string = _get_secret("AZURE_STORAGE_CONNECTION_STRING")
        self.azure_storage_container_name = _get_secret("AZURE_STORAGE_CONTAINER_NAME")

        # S3
        self.s3_bucket_name = _get_secret("S3_BUCKET_NAME")

        # Application Settings
        self.log_level = _get_secret("LOG_LEVEL", "INFO")
        max_file_size_str = _get_secret("MAX_FILE_SIZE_MB", "50")
        self.max_file_size_mb = int(max_file_size_str) if max_file_size_str else 50
        cache_enabled_str = _get_secret("CACHE_ENABLED", "true")
        self.cache_enabled = cache_enabled_str.lower() in ("true", "1", "yes") if cache_enabled_str else True

        # Paths
        self.default_upload_path = _get_secret("DEFAULT_UPLOAD_PATH", "./uploads")
        self.default_output_path = _get_secret("DEFAULT_OUTPUT_PATH", "./outputs")


@lru_cache()
def get_settings() -> Settings:
    """Retorna uma instância singleton das configurações."""
    return Settings()

