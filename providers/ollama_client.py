"""Provider para integração com Ollama (modelos locais)."""

from typing import Optional

import httpx
import structlog

from .base_provider import BaseLLMProvider

logger = structlog.get_logger()


class OllamaProvider(BaseLLMProvider):
    """Provider para integração com Ollama (modelos locais)."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Inicializa o provider Ollama."""
        super().__init__(api_key, base_url)
        self.base_url = base_url or "http://localhost:11434"

    async def generate_response(
        self,
        prompt: str,
        model: str = "llama2",
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> str:
        """
        Gera resposta usando Ollama API.

        Args:
            prompt: Texto de entrada
            model: Nome do modelo (padrão: llama2)
            max_tokens: Número máximo de tokens
            **kwargs: Argumentos adicionais

        Returns:
            Resposta gerada
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            **kwargs,
        }

        if max_tokens:
            payload["options"] = {"num_predict": max_tokens}

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")

        except httpx.HTTPError as e:
            logger.error("Erro ao chamar Ollama API", error=str(e))
            raise ValueError(f"Erro ao chamar Ollama: {e}")

    async def list_models(self) -> list[str]:
        """Lista modelos disponíveis no Ollama."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                result = response.json()
                return [model["name"] for model in result.get("models", [])]
        except Exception as e:
            logger.warning("Erro ao listar modelos Ollama", error=str(e))
            return self.get_available_models()

    def get_available_models(self) -> list[str]:
        """Retorna lista de modelos Ollama comuns."""
        return [
            "llama2",
            "llama2:13b",
            "llama2:70b",
            "mistral",
            "codellama",
            "phi",
        ]

