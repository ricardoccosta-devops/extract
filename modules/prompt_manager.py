"""Módulo para gerenciamento de prompts pré-definidos e templates."""

from typing import Dict


class PromptManager:
    """Gerenciador de prompts pré-definidos para extração de informações."""

    # Prompts pré-definidos para diferentes casos de uso
    PREDEFINED_PROMPTS: Dict[str, str] = {
        "Resumo": "Forneça um resumo detalhado e estruturado do seguinte documento. Inclua os pontos principais, conclusões e informações relevantes:\n\n{content}",
        
        "Extrair Informações Principais": "Extraia as informações principais do documento abaixo. Liste os pontos mais importantes de forma organizada:\n\n{content}",
        
        "Análise de Dados": "Analise o documento e extraia todos os dados numéricos, datas, métricas, valores financeiros e estatísticas importantes. Organize em uma lista estruturada:\n\n{content}",
        
        "Perguntas e Respostas": "Leia cuidadosamente o documento e responda às seguintes perguntas de forma clara e objetiva:\n1. Qual é o assunto principal do documento?\n2. Quais são as conclusões apresentadas?\n3. Quais são as recomendações ou próximos passos?\n4. Quais são os pontos-chave que devem ser destacados?\n\nDocumento:\n{content}",
        
        "Estrutura do Documento": "Identifique e descreva a estrutura do documento, incluindo:\n- Seções principais e subtópicos\n- Organização do conteúdo\n- Hierarquia de informações\n- Fluxo lógico do documento\n\nDocumento:\n{content}",
        
        "Extrair Entidades": "Extraia do documento todas as entidades importantes, organizando-as por categoria:\n- Nomes de pessoas\n- Organizações e empresas\n- Locais e endereços\n- Datas e períodos\n- Valores monetários e números\n- Termos técnicos e conceitos-chave\n\nDocumento:\n{content}",
        
        "Análise de Sentimento": "Analise o tom e sentimento do documento. Identifique:\n- Tom geral (positivo, neutro, negativo)\n- Linguagem utilizada\n- Pontos de destaque emocional\n- Recomendações ou críticas apresentadas\n\nDocumento:\n{content}",
        
        "Extrair Ações e Tarefas": "Identifique e liste todas as ações, tarefas, responsabilidades e próximos passos mencionados no documento:\n\n{content}",
        
        "Comparação e Contraste": "Se o documento contém comparações ou contrastes, identifique e descreva:\n- Elementos comparados\n- Diferenças e semelhanças\n- Conclusões das comparações\n\nDocumento:\n{content}",
        
        "Resumo Executivo": "Crie um resumo executivo do documento, destacando:\n- Objetivo principal\n- Principais descobertas\n- Recomendações estratégicas\n- Impacto e implicações\n\nDocumento:\n{content}",
    }

    @classmethod
    def get_prompt(cls, prompt_name: str) -> str:
        """
        Retorna um prompt pré-definido pelo nome.

        Args:
            prompt_name: Nome do prompt pré-definido

        Returns:
            Template do prompt

        Raises:
            KeyError: Se o prompt não existir
        """
        if prompt_name not in cls.PREDEFINED_PROMPTS:
            raise KeyError(
                f"Prompt '{prompt_name}' não encontrado. "
                f"Prompts disponíveis: {', '.join(cls.PREDEFINED_PROMPTS.keys())}"
            )
        return cls.PREDEFINED_PROMPTS[prompt_name]

    @classmethod
    def list_prompts(cls) -> list[str]:
        """
        Retorna lista de nomes de prompts disponíveis.

        Returns:
            Lista de nomes de prompts
        """
        return list(cls.PREDEFINED_PROMPTS.keys())

    @classmethod
    def add_custom_prompt(cls, name: str, template: str) -> None:
        """
        Adiciona um prompt personalizado.

        Args:
            name: Nome do prompt
            template: Template do prompt (deve conter {content})
        """
        if "{content}" not in template:
            raise ValueError(
                "Template deve conter {content} como placeholder para o conteúdo do documento"
            )
        cls.PREDEFINED_PROMPTS[name] = template

    @classmethod
    def format_prompt(cls, template: str, content: str) -> str:
        """
        Formata um template de prompt com o conteúdo do documento.

        Args:
            template: Template do prompt
            content: Conteúdo do documento

        Returns:
            Prompt formatado
        """
        if "{content}" in template:
            return template.format(content=content)
        else:
            # Se não tem placeholder, adiciona o conteúdo no final
            return f"{template}\n\nDocumento:\n{content}"

