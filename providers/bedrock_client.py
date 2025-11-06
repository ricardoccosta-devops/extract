"""Provider para integração com AWS Bedrock."""

from typing import Optional

import boto3
import structlog
from botocore.exceptions import ClientError

from .base_provider import BaseLLMProvider

logger = structlog.get_logger()


class BedrockProvider(BaseLLMProvider):
    """Provider para integração com AWS Bedrock."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_region: Optional[str] = None,
    ):
        """Inicializa o provider AWS Bedrock."""
        super().__init__(api_key, base_url)
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_region = aws_region or "us-east-1"
        self._bedrock_client = None

    def _get_bedrock_client(self):
        """Retorna cliente Bedrock configurado."""
        if self._bedrock_client is None:
            self._bedrock_client = boto3.client(
                "bedrock-runtime",
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.aws_region,
            )
        return self._bedrock_client

    async def generate_response(
        self,
        prompt: str,
        model: str = "anthropic.claude-v2",
        max_tokens: Optional[int] = 4096,
        **kwargs,
    ) -> str:
        """
        Gera resposta usando AWS Bedrock.

        Args:
            prompt: Texto de entrada
            model: ID do modelo Bedrock
            max_tokens: Número máximo de tokens
            **kwargs: Argumentos adicionais

        Returns:
            Resposta gerada
        """
        if not self.aws_access_key_id or not self.aws_secret_access_key:
            raise ValueError("Credenciais AWS não configuradas")

        import asyncio

        def _invoke_bedrock():
            client = self._get_bedrock_client()

            # Formato para Claude no Bedrock
            if "claude" in model.lower():
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens or 4096,
                    "messages": [{"role": "user", "content": prompt}],
                }
            else:
                # Formato genérico
                body = {
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": max_tokens or 4096,
                        **kwargs,
                    },
                }

            try:
                import json

                response = client.invoke_model(
                    modelId=model,
                    body=json.dumps(body),
                    contentType="application/json",
                    accept="application/json",
                )

                response_body = json.loads(response["body"].read())

                if "claude" in model.lower():
                    return response_body["content"][0]["text"]
                else:
                    return response_body.get("results", [{}])[0].get(
                        "outputText", ""
                    )

            except ClientError as e:
                logger.error("Erro ao chamar Bedrock", error=str(e))
                raise ValueError(f"Erro ao chamar Bedrock: {e}")

        # Executa em thread pool para não bloquear
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _invoke_bedrock)

    def get_available_models(self) -> list[str]:
        """Retorna lista de modelos Bedrock disponíveis."""
        return [
            "anthropic.claude-v2",
            "anthropic.claude-v2:1",
            "anthropic.claude-instant-v1",
            "amazon.titan-text-lite-v1",
            "amazon.titan-text-express-v1",
            "ai21.j2-ultra",
            "ai21.j2-mid",
        ]

