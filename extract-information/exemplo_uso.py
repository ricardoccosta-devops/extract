"""Script de exemplo para uso programático da plataforma."""

import asyncio
from modules.file_ingestion import FileIngestionService, FileSource
from modules.file_processing import FileProcessingService
from modules.output_formatter import OutputFormatterService
from modules.llm_manager import LLMManager


async def exemplo_processamento():
    """Exemplo de processamento de arquivo."""
    
    # Inicializa serviços
    ingestion_service = FileIngestionService()
    processing_service = FileProcessingService()
    formatter_service = OutputFormatterService()
    llm_manager = LLMManager()
    
    # Exemplo 1: Processar arquivo local
    print("Exemplo 1: Processando arquivo local...")
    try:
        file_content, file_name = await ingestion_service.ingest_file(
            FileSource.LOCAL_PATH,
            file_path="./exemplo.pdf"  # Substitua pelo caminho do seu arquivo
        )
        
        processed_doc = processing_service.process_file(file_content, file_name)
        
        # Formata como JSON
        json_output = formatter_service.format_output(processed_doc, "json")
        print(f"Conteúdo extraído ({len(processed_doc.content)} caracteres)")
        print(f"Metadados: {processed_doc.metadata}")
        
    except FileNotFoundError:
        print("Arquivo não encontrado. Pule este exemplo.")
    
    # Exemplo 2: Processar com LLM
    print("\nExemplo 2: Processando com LLM...")
    try:
        # Primeiro processa o arquivo
        file_content, file_name = await ingestion_service.ingest_file(
            FileSource.LOCAL_PATH,
            file_path="./exemplo.txt"
        )
        processed_doc = processing_service.process_file(file_content, file_name)
        
        # Processa com LLM (requer configuração no .env)
        llm_response = await llm_manager.process_with_llm(
            content=processed_doc.content[:1000],  # Limita para exemplo
            provider_name="openai",
            model="gpt-3.5-turbo",
            prompt_template="Resuma o seguinte texto em 3 frases:\n\n{content}"
        )
        
        print(f"Resposta do LLM: {llm_response}")
        
    except Exception as e:
        print(f"Erro ao processar com LLM: {e}")
        print("Certifique-se de ter configurado as chaves de API no .env")


if __name__ == "__main__":
    asyncio.run(exemplo_processamento())

