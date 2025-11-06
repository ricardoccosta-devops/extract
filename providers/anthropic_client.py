"""Provider para integração com Anthropic (Claude)."""

from typing import Optional

import httpx
import structlog

from .base_provider import BaseLLMProvider

logger = structlog.get_logger()


class AnthropicProvider(BaseLLMProvider):
    """Provider para integração com Anthropic API."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Inicializa o provider Anthropic."""
        super().__init__(api_key, base_url)
        self.base_url = base_url or "https://api.anthropic.com/v1"

    async def generate_response(
        self,
        prompt: str,
        model: str = "claude-3-opus-20240229",
        max_tokens: Optional[int] = 4096,
        **kwargs,
    ) -> str:
        """
        Gera resposta usando Anthropic API.

        Args:
            prompt: Texto de entrada
            model: Nome do modelo (padrão: claude-3-opus-20240229)
            max_tokens: Número máximo de tokens
            **kwargs: Argumentos adicionais

        Returns:
            Resposta gerada
        """
        if not self.api_key:
            raise ValueError("Anthropic API key não configurada")

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens or 4096,
            **kwargs,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                return result["content"][0]["text"]

        except httpx.HTTPError as e:
            logger.error("Erro ao chamar Anthropic API", error=str(e))
            raise ValueError(f"Erro ao chamar Anthropic: {e}")

    def get_available_models(self) -> list[str]:
        """Retorna lista de modelos Anthropic disponíveis."""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]

