"""Módulo para salvamento de arquivos processados em múltiplos destinos."""

import os
from enum import Enum
from pathlib import Path
from typing import Optional

import aiofiles
import structlog
from azure.storage.blob import BlobServiceClient
from botocore.exceptions import ClientError

from config import get_settings

logger = structlog.get_logger()


class StorageDestination(str, Enum):
    """Tipos de destinos de armazenamento suportados."""

    LOCAL = "local"
    NETWORK_PATH = "network_path"
    S3 = "s3"
    AZURE = "azure"


class FileStorageService:
    """Serviço para salvamento de arquivos processados em múltiplos destinos."""

    def __init__(self):
        """Inicializa o serviço de armazenamento."""
        self.settings = get_settings()
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Garante que os diretórios necessários existam."""
        Path(self.settings.default_output_path).mkdir(parents=True, exist_ok=True)

    async def save_file(
        self,
        content: str,
        file_name: str,
        destination: StorageDestination,
        destination_path: Optional[str] = None,
        bucket_name: Optional[str] = None,
        object_key: Optional[str] = None,
        container_name: Optional[str] = None,
        blob_name: Optional[str] = None,
    ) -> str:
        """
        Salva um arquivo processado no destino especificado.

        Args:
            content: Conteúdo do arquivo a ser salvo (string)
            file_name: Nome do arquivo
            destination: Tipo de destino (local, network_path, s3, azure)
            destination_path: Caminho do destino (para local/network_path)
            bucket_name: Nome do bucket (para S3)
            object_key: Chave do objeto (para S3)
            container_name: Nome do container (para Azure)
            blob_name: Nome do blob (para Azure)

        Returns:
            Caminho ou URI do arquivo salvo

        Raises:
            ValueError: Se os parâmetros forem inválidos
            IOError: Se houver erro ao salvar o arquivo
        """
        logger.info(
            "Iniciando salvamento de arquivo",
            destination=destination.value,
            file_name=file_name,
        )

        try:
            if destination == StorageDestination.LOCAL:
                if destination_path is None:
                    destination_path = self.settings.default_output_path
                return await self._save_to_local(content, file_name, destination_path)

            elif destination == StorageDestination.NETWORK_PATH:
                if destination_path is None:
                    raise ValueError("destination_path é obrigatório para network_path")
                return await self._save_to_network(content, file_name, destination_path)

            elif destination == StorageDestination.S3:
                if bucket_name is None or object_key is None:
                    raise ValueError(
                        "bucket_name e object_key são obrigatórios para S3"
                    )
                return await self._save_to_s3(content, file_name, bucket_name, object_key)

            elif destination == StorageDestination.AZURE:
                if container_name is None or blob_name is None:
                    raise ValueError(
                        "container_name e blob_name são obrigatórios para Azure"
                    )
                return await self._save_to_azure(
                    content, file_name, container_name, blob_name
                )

            else:
                raise ValueError(f"Destino não suportado: {destination}")

        except Exception as e:
            logger.error("Erro ao salvar arquivo", error=str(e), destination=destination.value)
            raise

    async def _save_to_local(
        self, content: str, file_name: str, destination_path: str
    ) -> str:
        """Salva um arquivo em um diretório local."""
        Path(destination_path).mkdir(parents=True, exist_ok=True)
        file_path = os.path.join(destination_path, file_name)

        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(content)

        logger.info("Arquivo salvo localmente", file_path=file_path, size=len(content))
        return file_path

    async def _save_to_network(
        self, content: str, file_name: str, network_path: str
    ) -> str:
        """Salva um arquivo em um diretório de rede."""
        # Verifica se o caminho de rede existe ou pode ser acessado
        if not os.path.exists(network_path):
            try:
                Path(network_path).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise IOError(
                    f"Não foi possível acessar ou criar o diretório de rede: {network_path}. "
                    f"Erro: {e}"
                )

        file_path = os.path.join(network_path, file_name)

        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(content)

        logger.info(
            "Arquivo salvo em diretório de rede",
            file_path=file_path,
            size=len(content),
        )
        return file_path

    async def _save_to_s3(
        self, content: str, file_name: str, bucket_name: str, object_key: str
    ) -> str:
        """Salva um arquivo no Amazon S3."""
        try:
            import boto3

            if not self.settings.aws_access_key_id or not self.settings.aws_secret_access_key:
                raise ValueError("Credenciais AWS não configuradas")

            s3_client = boto3.client(
                "s3",
                aws_access_key_id=self.settings.aws_access_key_id,
                aws_secret_access_key=self.settings.aws_secret_access_key,
                region_name=self.settings.aws_region,
            )

            # Converte string para bytes
            content_bytes = content.encode("utf-8")

            s3_client.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=content_bytes,
                ContentType="text/plain; charset=utf-8",
            )

            s3_uri = f"s3://{bucket_name}/{object_key}"

            logger.info(
                "Arquivo salvo no S3 com sucesso",
                bucket=bucket_name,
                key=object_key,
                size=len(content_bytes),
                uri=s3_uri,
            )
            return s3_uri

        except ClientError as e:
            logger.error("Erro ao salvar no S3", error=str(e))
            raise IOError(f"Erro ao salvar arquivo no S3: {e}")
        except Exception as e:
            logger.error("Erro inesperado ao salvar no S3", error=str(e))
            raise

    async def _save_to_azure(
        self, content: str, file_name: str, container_name: str, blob_name: str
    ) -> str:
        """Salva um arquivo no Azure Blob Storage."""
        try:
            if not self.settings.azure_storage_connection_string:
                raise ValueError("Azure Storage connection string não configurada")

            blob_service_client = BlobServiceClient.from_connection_string(
                self.settings.azure_storage_connection_string
            )

            # Garante que o container existe
            container_client = blob_service_client.get_container_client(container_name)
            if not container_client.exists():
                container_client.create_container()

            blob_client = blob_service_client.get_blob_client(
                container=container_name, blob=blob_name
            )

            # Converte string para bytes
            content_bytes = content.encode("utf-8")

            blob_client.upload_blob(
                content_bytes,
                overwrite=True,
                content_settings={"content_type": "text/plain; charset=utf-8"},
            )

            blob_uri = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}"

            logger.info(
                "Arquivo salvo no Azure com sucesso",
                container=container_name,
                blob=blob_name,
                size=len(content_bytes),
                uri=blob_uri,
            )
            return blob_uri

        except Exception as e:
            logger.error("Erro ao salvar no Azure", error=str(e))
            raise IOError(f"Erro ao salvar arquivo no Azure: {e}")

    async def save_multiple_files(
        self,
        files: list[tuple[str, str]],
        destination: StorageDestination,
        destination_path: Optional[str] = None,
        bucket_name: Optional[str] = None,
        container_name: Optional[str] = None,
        prefix: Optional[str] = None,
    ) -> list[str]:
        """
        Salva múltiplos arquivos simultaneamente.

        Args:
            files: Lista de tuplas (conteúdo, nome_arquivo)
            destination: Tipo de destino
            destination_path: Caminho base (para local/network_path)
            bucket_name: Nome do bucket (para S3)
            container_name: Nome do container (para Azure)
            prefix: Prefixo para os nomes dos arquivos (para S3/Azure)

        Returns:
            Lista de caminhos/URIs dos arquivos salvos
        """
        logger.info(
            "Iniciando salvamento de múltiplos arquivos",
            count=len(files),
            destination=destination.value,
        )

        saved_paths = []

        for content, file_name in files:
            try:
                if destination == StorageDestination.S3:
                    object_key = f"{prefix}/{file_name}" if prefix else file_name
                    path = await self._save_to_s3(
                        content, file_name, bucket_name, object_key
                    )
                elif destination == StorageDestination.AZURE:
                    blob_name = f"{prefix}/{file_name}" if prefix else file_name
                    path = await self._save_to_azure(
                        content, file_name, container_name, blob_name
                    )
                else:
                    path = await self.save_file(
                        content, file_name, destination, destination_path
                    )
                saved_paths.append(path)
            except Exception as e:
                logger.error(
                    "Erro ao salvar arquivo",
                    error=str(e),
                    file_name=file_name,
                )
                # Continua salvando os outros arquivos mesmo se um falhar

        logger.info(
            "Salvamento de múltiplos arquivos concluído",
            saved=len(saved_paths),
            total=len(files),
        )
        return saved_paths

