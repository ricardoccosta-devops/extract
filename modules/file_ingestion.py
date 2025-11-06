"""Módulo de ingestão de arquivos de múltiplas fontes."""

import asyncio
import os
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple

import aiofiles
import structlog
from azure.storage.blob import BlobServiceClient
from botocore.exceptions import ClientError

from config import get_settings

logger = structlog.get_logger()


class FileSource(str, Enum):
    """Tipos de fontes de arquivo suportadas."""

    UPLOAD = "upload"
    LOCAL_PATH = "local_path"
    NETWORK_PATH = "network_path"
    S3 = "s3"
    AZURE = "azure"


class FileIngestionService:
    """Serviço para ingestão de arquivos de múltiplas fontes."""

    def __init__(self):
        """Inicializa o serviço de ingestão."""
        self.settings = get_settings()
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Garante que os diretórios necessários existam."""
        Path(self.settings.default_upload_path).mkdir(parents=True, exist_ok=True)
        Path(self.settings.default_output_path).mkdir(parents=True, exist_ok=True)

    async def ingest_file(
        self,
        source: FileSource,
        file_path: Optional[str] = None,
        file_content: Optional[bytes] = None,
        file_name: Optional[str] = None,
        bucket_name: Optional[str] = None,
        object_key: Optional[str] = None,
    ) -> Tuple[bytes, str]:
        """
        Ingere um arquivo de uma fonte específica.

        Args:
            source: Tipo de fonte do arquivo
            file_path: Caminho do arquivo (para local_path, network_path)
            file_content: Conteúdo do arquivo em bytes (para upload)
            file_name: Nome do arquivo (para upload)
            bucket_name: Nome do bucket (para S3/Azure)
            object_key: Chave do objeto (para S3/Azure)

        Returns:
            Tupla contendo (conteúdo do arquivo em bytes, nome do arquivo)

        Raises:
            FileNotFoundError: Se o arquivo não for encontrado
            ValueError: Se os parâmetros forem inválidos
        """
        logger.info(
            "Iniciando ingestão de arquivo",
            source=source.value,
            file_path=file_path,
            file_name=file_name,
        )

        try:
            if source == FileSource.UPLOAD:
                if file_content is None:
                    raise ValueError("file_content é obrigatório para upload")
                if file_name is None:
                    raise ValueError("file_name é obrigatório para upload")
                return file_content, file_name

            elif source in [FileSource.LOCAL_PATH, FileSource.NETWORK_PATH]:
                if file_path is None:
                    raise ValueError("file_path é obrigatório para caminhos locais/rede")
                return await self._read_from_path(file_path)

            elif source == FileSource.S3:
                if bucket_name is None or object_key is None:
                    raise ValueError(
                        "bucket_name e object_key são obrigatórios para S3"
                    )
                return await self._read_from_s3(bucket_name, object_key)

            elif source == FileSource.AZURE:
                if bucket_name is None or object_key is None:
                    raise ValueError(
                        "bucket_name e object_key são obrigatórios para Azure"
                    )
                return await self._read_from_azure(bucket_name, object_key)

            else:
                raise ValueError(f"Fonte não suportada: {source}")

        except Exception as e:
            logger.error("Erro ao ingerir arquivo", error=str(e), source=source.value)
            raise

    async def _read_from_path(self, file_path: str) -> Tuple[bytes, str]:
        """Lê um arquivo de um caminho local ou de rede."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        async with aiofiles.open(file_path, "rb") as f:
            content = await f.read()
            file_name = os.path.basename(file_path)

        logger.info("Arquivo lido com sucesso", file_path=file_path, size=len(content))
        return content, file_name

    async def _read_from_s3(
        self, bucket_name: str, object_key: str
    ) -> Tuple[bytes, str]:
        """Lê um arquivo do Amazon S3."""
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

            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
            content = response["Body"].read()
            file_name = os.path.basename(object_key)

            logger.info(
                "Arquivo lido do S3 com sucesso",
                bucket=bucket_name,
                key=object_key,
                size=len(content),
            )
            return content, file_name

        except ClientError as e:
            logger.error("Erro ao ler do S3", error=str(e))
            raise FileNotFoundError(f"Erro ao ler arquivo do S3: {e}")

    async def _read_from_azure(
        self, container_name: str, blob_name: str
    ) -> Tuple[bytes, str]:
        """Lê um arquivo do Azure Blob Storage."""
        try:
            if not self.settings.azure_storage_connection_string:
                raise ValueError("Azure Storage connection string não configurada")

            blob_service_client = BlobServiceClient.from_connection_string(
                self.settings.azure_storage_connection_string
            )
            blob_client = blob_service_client.get_blob_client(
                container=container_name, blob=blob_name
            )

            content = blob_client.download_blob().readall()
            file_name = os.path.basename(blob_name)

            logger.info(
                "Arquivo lido do Azure com sucesso",
                container=container_name,
                blob=blob_name,
                size=len(content),
            )
            return content, file_name

        except Exception as e:
            logger.error("Erro ao ler do Azure", error=str(e))
            raise FileNotFoundError(f"Erro ao ler arquivo do Azure: {e}")

    async def ingest_multiple_files(
        self,
        source: FileSource,
        file_paths: Optional[List[str]] = None,
        file_contents: Optional[List[bytes]] = None,
        file_names: Optional[List[str]] = None,
    ) -> List[Tuple[bytes, str]]:
        """
        Ingere múltiplos arquivos simultaneamente.

        Args:
            source: Tipo de fonte dos arquivos
            file_paths: Lista de caminhos (para local_path, network_path)
            file_contents: Lista de conteúdos em bytes (para upload)
            file_names: Lista de nomes (para upload)

        Returns:
            Lista de tuplas (conteúdo, nome)
        """
        logger.info("Iniciando ingestão de múltiplos arquivos", count=len(file_paths or file_contents or []))

        if source == FileSource.UPLOAD:
            if file_contents is None or file_names is None:
                raise ValueError("file_contents e file_names são obrigatórios para upload")
            return list(zip(file_contents, file_names))

        elif source in [FileSource.LOCAL_PATH, FileSource.NETWORK_PATH]:
            if file_paths is None:
                raise ValueError("file_paths é obrigatório")
            tasks = [self._read_from_path(path) for path in file_paths]
            return await asyncio.gather(*tasks)

        else:
            raise ValueError(f"Ingestão múltipla não suportada para fonte: {source}")

