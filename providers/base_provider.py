"""Classe base abstrata para providers de LLM."""

from abc import ABC, abstractmethod
from typing import Optional


class BaseLLMProvider(ABC):
    """Interface base para todos os providers de LLM."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Inicializa o provider.

        Args:
            api_key: Chave de API do provider
            base_url: URL base do serviço
        """
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    async def generate_response(
        self, prompt: str, model: str, max_tokens: Optional[int] = None, **kwargs
    ) -> str:
        """
        Gera uma resposta do modelo de linguagem.

        Args:
            prompt: Texto de entrada para o modelo
            model: Nome do modelo a ser usado
            max_tokens: Número máximo de tokens na resposta
            **kwargs: Argumentos adicionais específicos do provider

        Returns:
            Resposta gerada pelo modelo
        """
        pass

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """
        Retorna lista de modelos disponíveis para este provider.

        Returns:
            Lista de nomes de modelos
        """
        pass

