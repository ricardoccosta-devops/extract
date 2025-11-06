# Plataforma de Processamento de Documentos

## 📋 Descrição

Plataforma inteligente de leitura e processamento de documentos com suporte a múltiplos formatos (PDF, TXT, DOC, PPT), múltiplas fontes (upload, caminhos locais/rede, S3, Azure) e integração com diversos Large Language Models (LLMs).

## 🚀 Instalação

### Pré-requisitos

- Python 3.11 ou superior
- pip

### Passos

1. Clone o repositório ou navegue até o diretório do projeto

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
# Copie o arquivo env.example para .env
cp env.example .env
# Ou no Windows:
copy env.example .env
# Edite o arquivo .env com suas chaves de API e configurações
```

## 🎯 Uso

Execute a aplicação Streamlit:

```bash
streamlit run main.py
```

A aplicação será aberta automaticamente no navegador em `http://localhost:8501`.

## 📁 Estrutura do Projeto

```
.
├── main.py                 # Ponto de entrada da aplicação
├── requirements.txt        # Dependências do projeto
├── .env.example           # Exemplo de variáveis de ambiente
├── config/                # Configurações centralizadas
│   ├── __init__.py
│   └── settings.py
├── modules/               # Módulos principais
│   ├── __init__.py
│   ├── file_ingestion.py  # Ingestão de arquivos
│   ├── file_processing.py # Processamento e extração
│   ├── output_formatter.py # Formatação de saída
│   ├── llm_manager.py     # Gerenciador de LLMs
│   └── prompt_manager.py  # Gerenciador de prompts
├── providers/            # Providers de LLM
│   ├── __init__.py
│   ├── base_provider.py
│   ├── openai_client.py
│   ├── anthropic_client.py
│   ├── ollama_client.py
│   └── bedrock_client.py
└── frontend/             # Interface Streamlit
    └── app.py
```

## ⚙️ Configuração

### Variáveis de Ambiente

Configure as seguintes variáveis no arquivo `.env`:

- **LLM Providers**: Configure as chaves de API dos providers que deseja usar
- **Cloud Storage**: Configure credenciais para S3 e/ou Azure (opcional)
- **Application Settings**: Ajuste limites e configurações da aplicação

### Formatos Suportados

- **Entrada**: PDF, TXT, DOCX, PPTX
- **Saída**: JSON, XML, CSV, TXT

### LLM Providers Suportados

- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Ollama (modelos locais)
- AWS Bedrock

## 🧩 Funcionalidades

- ✅ Upload múltiplo de arquivos
- ✅ Leitura de caminhos locais e de rede
- ✅ Integração com S3 e Azure Blob Storage
- ✅ Extração de texto de múltiplos formatos
- ✅ Processamento com LLMs (opcional)
- ✅ **Prompts personalizados para extração de informações**
- ✅ Prompts pré-definidos para casos de uso comuns
- ✅ Exportação em múltiplos formatos
- ✅ Cache para melhor performance
- ✅ Logging estruturado
- ✅ Interface intuitiva com Streamlit

## 📝 Exemplos de Uso

### Processamento Simples

1. Selecione "Upload" como fonte
2. Faça upload de um arquivo PDF
3. Escolha o formato de saída (ex: JSON)
4. Clique em "Processar Arquivos"
5. Baixe o resultado formatado

### Processamento com LLM e Prompts Personalizados

1. Ative a opção "Usar LLM para análise"
2. Selecione um provider (ex: OpenAI)
3. Escolha um modelo (ex: gpt-3.5-turbo)
4. **Configure seu prompt:**
   - **Modo Pré-definido**: Escolha entre prompts pré-configurados como:
     - Resumo
     - Extrair Informações Principais
     - Análise de Dados
     - Perguntas e Respostas
     - Estrutura do Documento
     - Extrair Entidades
     - E outros...
   - **Modo Personalizado**: Digite seu próprio prompt ou pergunta
     - Use `{content}` como placeholder para o conteúdo do documento
     - Exemplo: "Extraia todas as datas importantes e eventos mencionados no documento:\n\n{content}"
5. Processe o arquivo normalmente
6. Veja a análise do LLM na aba "Resultados", incluindo o prompt utilizado

## 🔧 Desenvolvimento

### Estrutura Modular

A aplicação segue uma arquitetura modular que permite:

- Adicionar novos formatos de arquivo facilmente
- Integrar novos providers de LLM
- Adicionar novos formatos de saída
- Modificar módulos sem impactar outros

### Adicionar um Novo Provider de LLM

1. Crie um novo arquivo em `providers/` (ex: `new_provider.py`)
2. Implemente a classe herdando de `BaseLLMProvider`
3. Implemente os métodos `generate_response()` e `get_available_models()`
4. Adicione o provider ao `LLMManager`

## 📄 Licença

Este projeto é fornecido como está, para uso interno.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

