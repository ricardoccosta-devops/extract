"""Gerenciador de LLM providers."""

from typing import Optional

import structlog

from config import get_settings
from providers import (
    AnthropicProvider,
    BaseLLMProvider,
    BedrockProvider,
    OllamaProvider,
    OpenAIProvider,
)

logger = structlog.get_logger()


class LLMManager:
    """Gerenciador centralizado para providers de LLM."""

    def __init__(self):
        """Inicializa o gerenciador de LLM."""
        self.settings = get_settings()
        self._providers: dict[str, BaseLLMProvider] = {}

    def get_provider(self, provider_name: str) -> BaseLLMProvider:
        """
        Retorna um provider específico.

        Args:
            provider_name: Nome do provider (openai, anthropic, ollama, bedrock)

        Returns:
            Instância do provider

        Raises:
            ValueError: Se o provider não for suportado
        """
        provider_name = provider_name.lower()

        if provider_name in self._providers:
            return self._providers[provider_name]

        if provider_name == "openai":
            provider = OpenAIProvider(
                api_key=self.settings.openai_api_key,
                base_url=self.settings.openai_base_url,
            )
        elif provider_name == "anthropic":
            provider = AnthropicProvider(
                api_key=self.settings.anthropic_api_key,
                base_url=self.settings.anthropic_base_url,
            )
        elif provider_name == "ollama":
            provider = OllamaProvider(base_url=self.settings.ollama_base_url)
        elif provider_name == "bedrock":
            provider = BedrockProvider(
                aws_access_key_id=self.settings.aws_access_key_id,
                aws_secret_access_key=self.settings.aws_secret_access_key,
                aws_region=self.settings.aws_region,
            )
        else:
            raise ValueError(
                f"Provider não suportado: {provider_name}. "
                "Providers disponíveis: openai, anthropic, ollama, bedrock"
            )

        self._providers[provider_name] = provider
        return provider

    def get_available_providers(self) -> list[str]:
        """Retorna lista de providers disponíveis."""
        return ["openai", "anthropic", "ollama", "bedrock"]

    async def process_with_llm(
        self,
        content: str,
        provider_name: str,
        model: str,
        prompt_template: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Processa conteúdo usando um LLM.

        Args:
            content: Conteúdo a ser processado
            provider_name: Nome do provider
            model: Nome do modelo
            prompt_template: Template do prompt (opcional). Use {content} como placeholder.
                           Se não fornecido, usa um prompt padrão de resumo.
            max_tokens: Número máximo de tokens

        Returns:
            Resposta do LLM
        """
        provider = self.get_provider(provider_name)

        if prompt_template:
            # Se o usuário forneceu um prompt, usa ele
            # Se não contém {content}, adiciona o conteúdo no final
            if "{content}" in prompt_template:
                prompt = prompt_template.format(content=content)
            else:
                prompt = f"{prompt_template}\n\nDocumento:\n{content}"
        else:
            # Prompt padrão se nenhum for fornecido
            prompt = f"Analise o seguinte documento e forneça um resumo detalhado:\n\n{content}"

        logger.info(
            "Processando com LLM",
            provider=provider_name,
            model=model,
            content_length=len(content),
            has_custom_prompt=prompt_template is not None,
        )

        return await provider.generate_response(
            prompt=prompt, model=model, max_tokens=max_tokens
        )

