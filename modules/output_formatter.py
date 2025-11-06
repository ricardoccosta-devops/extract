"""Módulo de formatação de saída em múltiplos formatos."""

import csv
import io
import json
from typing import Any, Dict

import structlog
from xml.dom import minidom
from xml.etree.ElementTree import Element, tostring

from modules.file_processing import ProcessedDocument

logger = structlog.get_logger()


class OutputFormatterService:
    """Serviço para formatação de saída em múltiplos formatos."""

    def __init__(self):
        """Inicializa o serviço de formatação."""
        self.logger = logger

    def format_output(
        self, document: ProcessedDocument, output_format: str
    ) -> str:
        """
        Formata o documento processado no formato especificado.

        Args:
            document: Documento processado
            output_format: Formato de saída (json, xml, csv, txt)

        Returns:
            String formatada no formato especificado

        Raises:
            ValueError: Se o formato não for suportado
        """
        output_format = output_format.lower()

        if output_format == "json":
            return self._format_as_json(document)
        elif output_format == "xml":
            return self._format_as_xml(document)
        elif output_format == "csv":
            return self._format_as_csv(document)
        elif output_format == "txt":
            return self._format_as_txt(document)
        else:
            raise ValueError(
                f"Formato não suportado: {output_format}. "
                "Formatos suportados: json, xml, csv, txt"
            )

    def _format_as_json(self, document: ProcessedDocument) -> str:
        """Formata o documento como JSON."""
        data = {
            "file_name": document.file_name,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "processed_at": document.processed_at.isoformat(),
            "content": document.content,
            "metadata": document.metadata,
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    def _format_as_xml(self, document: ProcessedDocument) -> str:
        """Formata o documento como XML."""
        root = Element("document")

        # Informações básicas
        file_info = Element("file_info")
        file_info.set("name", document.file_name)
        file_info.set("type", document.file_type)
        file_info.set("size", str(document.file_size))
        file_info.set("processed_at", document.processed_at.isoformat())
        root.append(file_info)

        # Conteúdo
        content_elem = Element("content")
        content_elem.text = document.content
        root.append(content_elem)

        # Metadados
        metadata_elem = Element("metadata")
        self._dict_to_xml(document.metadata, metadata_elem)
        root.append(metadata_elem)

        # Formatação bonita
        return self._prettify_xml(root)

    def _dict_to_xml(self, d: Dict[str, Any], parent: Element) -> None:
        """Converte um dicionário em elementos XML recursivamente."""
        for key, value in d.items():
            if isinstance(value, dict):
                child = Element(str(key))
                self._dict_to_xml(value, child)
                parent.append(child)
            elif isinstance(value, list):
                for item in value:
                    child = Element(str(key))
                    if isinstance(item, dict):
                        self._dict_to_xml(item, child)
                    else:
                        child.text = str(item)
                    parent.append(child)
            else:
                child = Element(str(key))
                child.text = str(value)
                parent.append(child)

    def _prettify_xml(self, elem: Element) -> str:
        """Formata XML de forma legível."""
        rough_string = tostring(elem, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def _format_as_csv(self, document: ProcessedDocument) -> str:
        """Formata o documento como CSV."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Cabeçalho
        writer.writerow(["Campo", "Valor"])

        # Informações básicas
        writer.writerow(["Nome do Arquivo", document.file_name])
        writer.writerow(["Tipo do Arquivo", document.file_type])
        writer.writerow(["Tamanho (bytes)", document.file_size])
        writer.writerow(["Processado em", document.processed_at.isoformat()])
        writer.writerow([])

        # Conteúdo
        writer.writerow(["Conteúdo"])
        # Divide o conteúdo em linhas para melhor legibilidade
        for line in document.content.split("\n"):
            writer.writerow([line])
        writer.writerow([])

        # Metadados
        writer.writerow(["Metadados"])
        for key, value in document.metadata.items():
            if isinstance(value, dict):
                writer.writerow([key, json.dumps(value, ensure_ascii=False)])
            else:
                writer.writerow([key, str(value)])

        return output.getvalue()

    def _format_as_txt(self, document: ProcessedDocument) -> str:
        """Formata o documento como TXT."""
        lines = [
            "=" * 80,
            "DOCUMENTO PROCESSADO",
            "=" * 80,
            "",
            f"Nome do Arquivo: {document.file_name}",
            f"Tipo do Arquivo: {document.file_type}",
            f"Tamanho: {document.file_size} bytes ({document.file_size / (1024*1024):.2f} MB)",
            f"Processado em: {document.processed_at.isoformat()}",
            "",
            "-" * 80,
            "CONTEÚDO",
            "-" * 80,
            "",
            document.content,
            "",
            "-" * 80,
            "METADADOS",
            "-" * 80,
            "",
        ]

        # Adiciona metadados formatados
        for key, value in document.metadata.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                for sub_key, sub_value in value.items():
                    lines.append(f"  {sub_key}: {sub_value}")
            else:
                lines.append(f"{key}: {value}")

        return "\n".join(lines)

