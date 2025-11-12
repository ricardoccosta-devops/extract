"""Provider para integração com OpenAI."""

from typing import Optional

import httpx
import structlog

from .base_provider import BaseLLMProvider

logger = structlog.get_logger()


class OpenAIProvider(BaseLLMProvider):
    """Provider para integração com OpenAI API."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Inicializa o provider OpenAI."""
        super().__init__(api_key, base_url)
        self.base_url = base_url or "https://api.openai.com/v1"

    async def generate_response(
        self,
        prompt: str,
        model: str = "gpt-4o-2024-11-20",
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> str:
        """
        Gera resposta usando OpenAI API.

        Args:
            prompt: Texto de entrada
            model: Nome do modelo (padrão: gpt-4o-2024-11-20 - versão mais recente)
            max_tokens: Número máximo de tokens
            **kwargs: Argumentos adicionais

        Returns:
            Resposta gerada
        """
        if not self.api_key:
            raise ValueError("OpenAI API key não configurada")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            **kwargs,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]

        except httpx.HTTPError as e:
            logger.error("Erro ao chamar OpenAI API", error=str(e))
            raise ValueError(f"Erro ao chamar OpenAI: {e}")

    def get_available_models(self) -> list[str]:
        """Retorna lista de modelos OpenAI disponíveis (ordenados do mais recente para o mais antigo)."""
        return [
            # Modelos GPT-5 (quando disponíveis - preparado para futuro)
            "gpt-5",
            "gpt-5-turbo",
            "gpt-5-mini",
            # Modelos GPT-4o (versões mais recentes - 2024)
            "gpt-4o-2024-11-20",  # Versão mais recente do GPT-4o (novembro 2024)
            "gpt-4o-2024-08-06",  # Versão anterior do GPT-4o
            "gpt-4o",  # Alias para versão mais recente
            "gpt-4o-mini-2024-07-18",  # Versão mais recente do GPT-4o-mini
            "gpt-4o-mini",  # Alias para versão mais recente
            # Modelos GPT-4 Turbo
            "gpt-4-turbo-2024-04-09",  # Versão mais recente do GPT-4 Turbo
            "gpt-4-turbo-preview",
            "gpt-4-turbo",
            # Modelos GPT-4 (versões anteriores)
            "gpt-4-0613",
            "gpt-4-32k",
            "gpt-4",
            # Modelos GPT-3.5 (compatibilidade)
            "gpt-3.5-turbo-0125",  # Versão mais recente do GPT-3.5
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo",
        ]

