"""Interface Streamlit para a plataforma de processamento de documentos."""

import asyncio
import time
from io import StringIO
from typing import Optional

import streamlit as st
import structlog

from config import get_settings
from modules.file_ingestion import FileIngestionService, FileSource
from modules.file_processing import FileProcessingService
from modules.file_storage import FileStorageService, StorageDestination
from modules.llm_manager import LLMManager
from modules.output_formatter import OutputFormatterService
from modules.prompt_manager import PromptManager

# Configuração de logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)
logger = structlog.get_logger()

# Configuração da página
st.set_page_config(
    page_title="Plataforma de Processamento de Documentos",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Cache para serviços
@st.cache_resource
def get_services():
    """Retorna instâncias dos serviços (cacheado)."""
    return {
        "ingestion": FileIngestionService(),
        "processing": FileProcessingService(),
        "formatter": OutputFormatterService(),
        "llm_manager": LLMManager(),
        "storage": FileStorageService(),
    }


async def auto_save_processed_file(
    processed_doc,
    output_format: str,
    services: dict,
    auto_save: bool,
    save_destination: Optional[str],
    save_path: Optional[str],
    save_bucket: Optional[str],
    save_object_key: Optional[str],
    save_container: Optional[str],
    save_blob: Optional[str],
) -> Optional[str]:
    """
    Salva automaticamente um arquivo processado no destino configurado.
    
    Returns:
        Mensagem de sucesso ou None se não houver salvamento
    """
    if not auto_save or not save_destination:
        return None
    
    try:
        formatted_output = services["formatter"].format_output(
            processed_doc, output_format.lower()
        )
        output_file_name = f"{processed_doc.file_name}_{output_format.lower()}.{output_format.lower()}"
        
        if save_destination == "Local":
            saved_path = await services["storage"].save_file(
                content=formatted_output,
                file_name=output_file_name,
                destination=StorageDestination.LOCAL,
                destination_path=save_path,
            )
            return f"💾 Arquivo salvo automaticamente em: {saved_path}"
        
        elif save_destination == "Diretório de Rede":
            saved_path = await services["storage"].save_file(
                content=formatted_output,
                file_name=output_file_name,
                destination=StorageDestination.NETWORK_PATH,
                destination_path=save_path,
            )
            return f"💾 Arquivo salvo automaticamente em: {saved_path}"
        
        elif save_destination == "S3":
            if save_bucket and save_object_key:
                final_object_key = save_object_key if save_object_key.endswith(output_file_name) else f"{save_object_key}/{output_file_name}"
                saved_uri = await services["storage"].save_file(
                    content=formatted_output,
                    file_name=output_file_name,
                    destination=StorageDestination.S3,
                    bucket_name=save_bucket,
                    object_key=final_object_key,
                )
                return f"💾 Arquivo salvo automaticamente no S3: {saved_uri}"
        
        elif save_destination == "Azure Blob Storage":
            if save_container and save_blob:
                final_blob_name = save_blob if save_blob.endswith(output_file_name) else f"{save_blob}/{output_file_name}"
                saved_uri = await services["storage"].save_file(
                    content=formatted_output,
                    file_name=output_file_name,
                    destination=StorageDestination.AZURE,
                    container_name=save_container,
                    blob_name=final_blob_name,
                )
                return f"💾 Arquivo salvo automaticamente no Azure: {saved_uri}"
        
        return None
    except Exception as save_error:
        logger.error("Erro no salvamento automático", error=str(save_error))
        return f"⚠️ Arquivo processado, mas erro ao salvar automaticamente: {save_error}"


def main():
    """Função principal da interface Streamlit."""
    st.title("📄 Plataforma de Processamento de Documentos")
    st.markdown(
        "**Plataforma inteligente para leitura, processamento e análise de documentos**"
    )

    services = get_services()
    settings = get_settings()

    # Sidebar - Configurações
    with st.sidebar:
        st.header("⚙️ Configurações")

        # Seleção de fonte
        source_type = st.selectbox(
            "Fonte do Arquivo",
            options=["Upload", "Caminho Local/Rede", "S3", "Azure Blob Storage"],
        )

        # Seleção de LLM (opcional)
        use_llm = st.checkbox("Usar LLM para análise", value=False)
        llm_provider = None
        llm_model = None
        custom_prompt = None
        
        if use_llm:
            llm_provider = st.selectbox(
                "Provider LLM",
                options=services["llm_manager"].get_available_providers(),
            )
            try:
                provider = services["llm_manager"].get_provider(llm_provider)
                llm_model = st.selectbox(
                    "Modelo",
                    options=provider.get_available_models(),
                )
            except Exception as e:
                st.error(f"Erro ao carregar modelos: {e}")
                use_llm = False
            
            st.divider()
            st.markdown("### 💬 Prompt Personalizado")
            st.caption("Digite sua pergunta ou instrução para extração de informações do documento")
            
            # Opções de prompt pré-definidas
            prompt_mode = st.radio(
                "Modo de Prompt",
                options=["Personalizado", "Pré-definido"],
                horizontal=True,
                help="Escolha entre escrever seu próprio prompt ou usar um pré-definido"
            )
            
            if prompt_mode == "Pré-definido":
                predefined_prompts = PromptManager.PREDEFINED_PROMPTS
                
                selected_predefined = st.selectbox(
                    "Escolha um prompt pré-definido",
                    options=list(predefined_prompts.keys())
                )
                custom_prompt = predefined_prompts[selected_predefined]
                st.text_area(
                    "Prompt selecionado (você pode editar):",
                    value=custom_prompt,
                    height=150,
                    key="predefined_prompt_editor"
                )
                custom_prompt = st.session_state.predefined_prompt_editor
            else:
                custom_prompt = st.text_area(
                    "Digite seu prompt ou pergunta",
                    placeholder="Exemplo: Extraia todas as datas importantes e eventos mencionados no documento.\n\nUse {content} como placeholder para o conteúdo do documento.",
                    height=150,
                    help="Use {content} no seu prompt para inserir o conteúdo do documento automaticamente"
                )
            
            if custom_prompt and "{content}" not in custom_prompt:
                st.warning("💡 Dica: Use {content} no seu prompt para inserir o conteúdo do documento automaticamente")

        # Formato de saída
        output_format = st.selectbox(
            "Formato de Saída",
            options=["JSON", "XML", "CSV", "TXT"],
        )

        st.divider()
        st.markdown("### 💾 Salvamento Automático")
        auto_save = st.checkbox("Salvar arquivos processados automaticamente", value=False)
        save_destination = None
        save_path = None
        save_bucket = None
        save_object_key = None
        save_container = None
        save_blob = None

        if auto_save:
            save_destination = st.selectbox(
                "Destino de Salvamento",
                options=["Local", "Diretório de Rede", "S3", "Azure Blob Storage"],
            )

            if save_destination == "Local":
                save_path = st.text_input(
                    "Caminho Local",
                    value=settings.default_output_path,
                    help="Caminho onde os arquivos serão salvos localmente",
                )
            elif save_destination == "Diretório de Rede":
                save_path = st.text_input(
                    "Caminho de Rede",
                    placeholder="\\\\server\\share\\... ou /mnt/network/...",
                    help="Caminho do diretório de rede onde os arquivos serão salvos",
                )
            elif save_destination == "S3":
                col1, col2 = st.columns(2)
                with col1:
                    save_bucket = st.text_input("Nome do Bucket S3")
                with col2:
                    save_object_key = st.text_input(
                        "Chave do Objeto (Object Key)",
                        placeholder="outputs/arquivo.json",
                        help="Chave do objeto no S3 (pode incluir prefixo/pasta)",
                    )
            elif save_destination == "Azure Blob Storage":
                col1, col2 = st.columns(2)
                with col1:
                    save_container = st.text_input("Nome do Container")
                with col2:
                    save_blob = st.text_input(
                        "Nome do Blob",
                        placeholder="outputs/arquivo.json",
                        help="Nome do blob no Azure (pode incluir prefixo/pasta)",
                    )

        st.divider()
        st.markdown("### 📊 Estatísticas")
        if "stats" in st.session_state:
            st.metric("Arquivos Processados", st.session_state.stats.get("processed", 0))
            st.metric("Tempo Médio", f"{st.session_state.stats.get('avg_time', 0):.2f}s")

    # Área principal
    tab1, tab2, tab3 = st.tabs(["📤 Upload/Processamento", "📊 Resultados", "📈 Logs"])

    with tab1:
        st.header("Upload e Processamento de Documentos")

        processed_documents = []

        if source_type == "Upload":
            uploaded_files = st.file_uploader(
                "Selecione um ou mais arquivos",
                type=["pdf", "txt", "docx", "pptx"],
                accept_multiple_files=True,
            )

            if uploaded_files:
                if st.button("🚀 Processar Arquivos", type="primary"):
                    with st.spinner("Processando arquivos..."):
                        start_time = time.time()

                        for uploaded_file in uploaded_files:
                            try:
                                # Verifica tamanho do arquivo
                                file_size_mb = len(uploaded_file.getvalue()) / (
                                    1024 * 1024
                                )
                                if file_size_mb > settings.max_file_size_mb:
                                    st.warning(
                                        f"Arquivo {uploaded_file.name} muito grande "
                                        f"({file_size_mb:.2f} MB). Limite: {settings.max_file_size_mb} MB"
                                    )
                                    continue

                                # Ingere arquivo
                                file_content = uploaded_file.getvalue()
                                file_name = uploaded_file.name

                                # Processa arquivo
                                processed_doc = services["processing"].process_file(
                                    file_content, file_name
                                )

                                # Processa com LLM se solicitado
                                if use_llm and llm_provider and llm_model:
                                    with st.spinner(
                                        f"Analisando com {llm_provider}..."
                                    ):
                                        llm_response = asyncio.run(
                                            services["llm_manager"].process_with_llm(
                                                content=processed_doc.content,
                                                provider_name=llm_provider,
                                                model=llm_model,
                                                prompt_template=custom_prompt if custom_prompt else None,
                                            )
                                        )
                                        processed_doc.metadata["llm_analysis"] = llm_response
                                        if custom_prompt:
                                            processed_doc.metadata["llm_prompt_used"] = custom_prompt

                                processed_documents.append(processed_doc)
                                st.success(f"✅ {file_name} processado com sucesso!")
                                
                                # Salvamento automático se configurado
                                save_message = asyncio.run(
                                    auto_save_processed_file(
                                        processed_doc,
                                        output_format,
                                        services,
                                        auto_save,
                                        save_destination,
                                        save_path,
                                        save_bucket,
                                        save_object_key,
                                        save_container,
                                        save_blob,
                                    )
                                )
                                if save_message:
                                    if save_message.startswith("⚠️"):
                                        st.warning(save_message)
                                    else:
                                        st.info(save_message)

                            except Exception as e:
                                st.error(f"❌ Erro ao processar {uploaded_file.name}: {e}")
                                logger.error("Erro ao processar arquivo", error=str(e))

                        elapsed_time = time.time() - start_time

                        # Atualiza estatísticas
                        if "stats" not in st.session_state:
                            st.session_state.stats = {"processed": 0, "total_time": 0}
                        st.session_state.stats["processed"] += len(processed_documents)
                        st.session_state.stats["total_time"] += elapsed_time
                        st.session_state.stats["avg_time"] = (
                            st.session_state.stats["total_time"]
                            / st.session_state.stats["processed"]
                        )

                        st.session_state.processed_documents = processed_documents
                        st.rerun()

        elif source_type == "Caminho Local/Rede":
            file_path = st.text_input(
                "Digite o caminho do arquivo ou diretório",
                placeholder="C:/Users/... ou \\\\server\\share\\...",
            )

            if st.button("🚀 Processar", type="primary"):
                if file_path:
                    with st.spinner("Processando..."):
                        try:
                            file_content, file_name = asyncio.run(
                                services["ingestion"].ingest_file(
                                    FileSource.LOCAL_PATH, file_path=file_path
                                )
                            )

                            processed_doc = services["processing"].process_file(
                                file_content, file_name
                            )

                            if use_llm and llm_provider and llm_model:
                                llm_response = asyncio.run(
                                    services["llm_manager"].process_with_llm(
                                        content=processed_doc.content,
                                        provider_name=llm_provider,
                                        model=llm_model,
                                        prompt_template=custom_prompt if custom_prompt else None,
                                    )
                                )
                                processed_doc.metadata["llm_analysis"] = llm_response
                                if custom_prompt:
                                    processed_doc.metadata["llm_prompt_used"] = custom_prompt

                            st.session_state.processed_documents = [processed_doc]
                            st.success("✅ Arquivo processado com sucesso!")
                            
                            # Salvamento automático se configurado
                            save_message = asyncio.run(
                                auto_save_processed_file(
                                    processed_doc,
                                    output_format,
                                    services,
                                    auto_save,
                                    save_destination,
                                    save_path,
                                    save_bucket,
                                    save_object_key,
                                    save_container,
                                    save_blob,
                                )
                            )
                            if save_message:
                                if save_message.startswith("⚠️"):
                                    st.warning(save_message)
                                else:
                                    st.info(save_message)
                            
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Erro: {e}")

        elif source_type == "S3":
            col1, col2 = st.columns(2)
            with col1:
                bucket_name = st.text_input("Nome do Bucket S3")
            with col2:
                object_key = st.text_input("Chave do Objeto (Object Key)")

            if st.button("🚀 Processar", type="primary"):
                if bucket_name and object_key:
                    with st.spinner("Baixando e processando do S3..."):
                        try:
                            file_content, file_name = asyncio.run(
                                services["ingestion"].ingest_file(
                                    FileSource.S3,
                                    bucket_name=bucket_name,
                                    object_key=object_key,
                                )
                            )

                            processed_doc = services["processing"].process_file(
                                file_content, file_name
                            )

                            if use_llm and llm_provider and llm_model:
                                llm_response = asyncio.run(
                                    services["llm_manager"].process_with_llm(
                                        content=processed_doc.content,
                                        provider_name=llm_provider,
                                        model=llm_model,
                                        prompt_template=custom_prompt if custom_prompt else None,
                                    )
                                )
                                processed_doc.metadata["llm_analysis"] = llm_response
                                if custom_prompt:
                                    processed_doc.metadata["llm_prompt_used"] = custom_prompt

                            st.session_state.processed_documents = [processed_doc]
                            st.success("✅ Arquivo processado com sucesso!")
                            
                            # Salvamento automático se configurado
                            save_message = asyncio.run(
                                auto_save_processed_file(
                                    processed_doc,
                                    output_format,
                                    services,
                                    auto_save,
                                    save_destination,
                                    save_path,
                                    save_bucket,
                                    save_object_key,
                                    save_container,
                                    save_blob,
                                )
                            )
                            if save_message:
                                if save_message.startswith("⚠️"):
                                    st.warning(save_message)
                                else:
                                    st.info(save_message)
                            
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Erro: {e}")

        elif source_type == "Azure Blob Storage":
            col1, col2 = st.columns(2)
            with col1:
                container_name = st.text_input("Nome do Container")
            with col2:
                blob_name = st.text_input("Nome do Blob")

            if st.button("🚀 Processar", type="primary"):
                if container_name and blob_name:
                    with st.spinner("Baixando e processando do Azure..."):
                        try:
                            file_content, file_name = asyncio.run(
                                services["ingestion"].ingest_file(
                                    FileSource.AZURE,
                                    bucket_name=container_name,
                                    object_key=blob_name,
                                )
                            )

                            processed_doc = services["processing"].process_file(
                                file_content, file_name
                            )

                            if use_llm and llm_provider and llm_model:
                                llm_response = asyncio.run(
                                    services["llm_manager"].process_with_llm(
                                        content=processed_doc.content,
                                        provider_name=llm_provider,
                                        model=llm_model,
                                    )
                                )
                                processed_doc.metadata["llm_analysis"] = llm_response

                            st.session_state.processed_documents = [processed_doc]
                            st.success("✅ Arquivo processado com sucesso!")
                            
                            # Salvamento automático se configurado
                            save_message = asyncio.run(
                                auto_save_processed_file(
                                    processed_doc,
                                    output_format,
                                    services,
                                    auto_save,
                                    save_destination,
                                    save_path,
                                    save_bucket,
                                    save_object_key,
                                    save_container,
                                    save_blob,
                                )
                            )
                            if save_message:
                                if save_message.startswith("⚠️"):
                                    st.warning(save_message)
                                else:
                                    st.info(save_message)
                            
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Erro: {e}")

    with tab2:
        st.header("Resultados do Processamento")

        if "processed_documents" in st.session_state:
            processed_docs = st.session_state.processed_documents

            for idx, doc in enumerate(processed_docs):
                with st.expander(
                    f"📄 {doc.file_name} ({doc.file_type}) - {doc.file_size / (1024*1024):.2f} MB",
                    expanded=idx == 0,
                ):
                    # Informações do arquivo
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Tamanho", f"{doc.file_size / (1024*1024):.2f} MB")
                    with col2:
                        st.metric("Tipo", doc.file_type)
                    with col3:
                        st.metric(
                            "Processado em",
                            doc.processed_at.strftime("%H:%M:%S"),
                        )

                    # Formata e exibe resultado
                    formatted_output = services["formatter"].format_output(
                        doc, output_format.lower()
                    )

                    st.subheader("Conteúdo Formatado")
                    st.code(formatted_output, language=output_format.lower())

                    # Botões de download e salvamento
                    col_download, col_save = st.columns(2)
                    
                    with col_download:
                        st.download_button(
                            label=f"⬇️ Baixar {output_format}",
                            data=formatted_output,
                            file_name=f"{doc.file_name}_{output_format.lower()}.{output_format.lower()}",
                            mime=f"application/{output_format.lower()}",
                            key=f"download_{idx}",
                        )
                    
                    with col_save:
                        # Opções de salvamento manual
                        with st.expander("💾 Salvar em...", expanded=False):
                            manual_save_dest = st.selectbox(
                                "Destino",
                                options=["Local", "Diretório de Rede", "S3", "Azure Blob Storage"],
                                key=f"manual_save_dest_{idx}",
                            )
                            
                            if manual_save_dest == "Local":
                                manual_path = st.text_input(
                                    "Caminho",
                                    value=settings.default_output_path,
                                    key=f"manual_path_local_{idx}",
                                )
                                if st.button("💾 Salvar", key=f"save_local_{idx}"):
                                    try:
                                        saved_path = asyncio.run(
                                            services["storage"].save_file(
                                                content=formatted_output,
                                                file_name=f"{doc.file_name}_{output_format.lower()}.{output_format.lower()}",
                                                destination=StorageDestination.LOCAL,
                                                destination_path=manual_path,
                                            )
                                        )
                                        st.success(f"✅ Arquivo salvo em: {saved_path}")
                                    except Exception as e:
                                        st.error(f"❌ Erro ao salvar: {e}")
                            
                            elif manual_save_dest == "Diretório de Rede":
                                manual_network_path = st.text_input(
                                    "Caminho de Rede",
                                    placeholder="\\\\server\\share\\...",
                                    key=f"manual_path_network_{idx}",
                                )
                                if st.button("💾 Salvar", key=f"save_network_{idx}"):
                                    try:
                                        saved_path = asyncio.run(
                                            services["storage"].save_file(
                                                content=formatted_output,
                                                file_name=f"{doc.file_name}_{output_format.lower()}.{output_format.lower()}",
                                                destination=StorageDestination.NETWORK_PATH,
                                                destination_path=manual_network_path,
                                            )
                                        )
                                        st.success(f"✅ Arquivo salvo em: {saved_path}")
                                    except Exception as e:
                                        st.error(f"❌ Erro ao salvar: {e}")
                            
                            elif manual_save_dest == "S3":
                                col_s3_1, col_s3_2 = st.columns(2)
                                with col_s3_1:
                                    manual_bucket = st.text_input(
                                        "Bucket",
                                        key=f"manual_bucket_{idx}",
                                    )
                                with col_s3_2:
                                    manual_key = st.text_input(
                                        "Object Key",
                                        value=f"outputs/{doc.file_name}_{output_format.lower()}.{output_format.lower()}",
                                        key=f"manual_key_{idx}",
                                    )
                                if st.button("💾 Salvar", key=f"save_s3_{idx}"):
                                    try:
                                        saved_uri = asyncio.run(
                                            services["storage"].save_file(
                                                content=formatted_output,
                                                file_name=f"{doc.file_name}_{output_format.lower()}.{output_format.lower()}",
                                                destination=StorageDestination.S3,
                                                bucket_name=manual_bucket,
                                                object_key=manual_key,
                                            )
                                        )
                                        st.success(f"✅ Arquivo salvo em: {saved_uri}")
                                    except Exception as e:
                                        st.error(f"❌ Erro ao salvar: {e}")
                            
                            elif manual_save_dest == "Azure Blob Storage":
                                col_az_1, col_az_2 = st.columns(2)
                                with col_az_1:
                                    manual_container = st.text_input(
                                        "Container",
                                        key=f"manual_container_{idx}",
                                    )
                                with col_az_2:
                                    manual_blob = st.text_input(
                                        "Blob Name",
                                        value=f"outputs/{doc.file_name}_{output_format.lower()}.{output_format.lower()}",
                                        key=f"manual_blob_{idx}",
                                    )
                                if st.button("💾 Salvar", key=f"save_azure_{idx}"):
                                    try:
                                        saved_uri = asyncio.run(
                                            services["storage"].save_file(
                                                content=formatted_output,
                                                file_name=f"{doc.file_name}_{output_format.lower()}.{output_format.lower()}",
                                                destination=StorageDestination.AZURE,
                                                container_name=manual_container,
                                                blob_name=manual_blob,
                                            )
                                        )
                                        st.success(f"✅ Arquivo salvo em: {saved_uri}")
                                    except Exception as e:
                                        st.error(f"❌ Erro ao salvar: {e}")

                    # Análise LLM se disponível
                    if "llm_analysis" in doc.metadata:
                        st.subheader("🤖 Análise LLM")
                        if "llm_prompt_used" in doc.metadata:
                            with st.expander("📝 Prompt Utilizado", expanded=False):
                                st.code(doc.metadata["llm_prompt_used"], language="text")
                        st.info(doc.metadata["llm_analysis"])

                    # Metadados detalhados
                    with st.expander("📋 Metadados Detalhados"):
                        st.json(doc.metadata)

        else:
            st.info("👆 Processe alguns arquivos na aba 'Upload/Processamento'")

    with tab3:
        st.header("Logs e Estatísticas")

        if "stats" in st.session_state:
            stats = st.session_state.stats
            st.metric("Total de Arquivos Processados", stats.get("processed", 0))
            st.metric("Tempo Total", f"{stats.get('total_time', 0):.2f}s")
            st.metric("Tempo Médio por Arquivo", f"{stats.get('avg_time', 0):.2f}s")

        st.subheader("Informações do Sistema")
        st.json(
            {
                "max_file_size_mb": settings.max_file_size_mb,
                "cache_enabled": settings.cache_enabled,
                "log_level": settings.log_level,
            }
        )


if __name__ == "__main__":
    main()

