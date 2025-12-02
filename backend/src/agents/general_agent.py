import json
import logging
from typing import Dict, Optional

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import kernel_function

from src.config.settings import settings
from src.services.general_service import GeneralService
from src.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

class GeneralPlugin:
    """Plugin for general inquiries, sales, and support."""
    
    @kernel_function(description="Busca respostas para perguntas frequentes (FAQ).")
    def search_faq(self, query: str) -> str:
        """
        Busca FAQ.
        Args:
            query: Pergunta ou termo de busca.
        """
        results = GeneralService.search_faq(query)
        if results:
            return json.dumps(results)
        return "Não encontrei uma resposta específica na FAQ."

    @kernel_function(description="Obtém informações institucionais da empresa.")
    def get_company_info(self, topic: str) -> str:
        """
        Info da empresa.
        Args:
            topic: Tópico (horário, endereço, contato).
        """
        return GeneralService.get_company_info(topic)

    @kernel_function(description="Lista todos os planos de internet e serviços disponíveis.")
    async def list_plans(self) -> str:
        """Lista planos."""
        plans = await GeneralService.list_plans()
        return json.dumps(plans)

    @kernel_function(description="Compara dois planos de internet.")
    async def compare_plans(self, plan_a: str, plan_b: str) -> str:
        """Compara planos."""
        return await GeneralService.compare_plans(plan_a, plan_b)

    @kernel_function(description="Busca 2ª via de fatura pelo email do cliente.")
    async def get_invoice_by_email(self, email: str) -> str:
        """Busca fatura por email."""
        return await GeneralService.get_invoice_by_email(email)

    @kernel_function(description="Retorna guia de solução de problemas de internet.")
    def troubleshoot_internet(self) -> str:
        """Guia de troubleshooting."""
        return GeneralService.troubleshoot_internet()

    @kernel_function(description="Verifica status do cliente pelo email (se já existe, plano atual, faturas).")
    async def check_client_status(self, email: str) -> str:
        """Verifica cliente."""
        result = await GeneralService.get_client_summary_by_email(email)
        return json.dumps(result)

    @kernel_function(description="Realiza a contratação completa (Cliente + Contrato + Boleto).")
    async def create_subscription(self, nome: str, email: str, plano_nome: str, cpf: str, endereco: str, telefone: str = "11999999999") -> str:
        """Cria assinatura."""
        result = await SubscriptionService.create_subscription(nome, email, plano_nome, cpf, endereco, telefone)
        return json.dumps(result)

class GeneralAgent:
    """
    Agent specialized in general inquiries, sales, and basic support.
    """
    
    SYSTEM_PROMPT = """Você é o Agente Geral (Atendimento Online) da Central de Atendimento.
    Sua missão é ser o primeiro ponto de contato, ajudando visitantes e clientes com dúvidas, vendas e suporte básico.
    
    PERSONA:
    - Nome: "Assistente Virtual"
    - Tom: Profissional, eficiente e focado em resolver.
    - Objetivo: Vender planos ou resolver problemas no primeiro contato.

    FERRAMENTAS OBRIGATÓRIAS:
    1. `list_plans`: USE SEMPRE que perguntarem "quais planos", "preços" ou "velocidades". NUNCA invente planos. Use APENAS o que retornar desta função.
    2. `check_client_status`: USE SEMPRE que o cliente disser "já sou cliente", "meu email é..." ou pedir algo que exija cadastro.
    3. `create_subscription`: USE APENAS quando o cliente confirmar explicitamente a contratação e fornecer TODOS os dados (Nome, Email, CPF, Endereço, Plano).
    4. `get_invoice_by_email`: Para 2ª via rápida.
    5. `troubleshoot_internet`: Para suporte técnico básico.

    FLUXO DE VENDAS (NOVO CLIENTE):
    1. O cliente demonstra interesse.
    2. Você CHAMA `list_plans` e apresenta as opções.
    3. O cliente escolhe um plano.
    4. Você pede os dados: "Para prosseguir, preciso do seu Nome Completo, CPF, Endereço, Telefone e E-mail."
    5. O cliente fornece os dados.
    6. Você CHAMA `create_subscription(nome, email, plano, cpf, endereco, telefone)`.
    7. Você apresenta o resultado: "Sucesso! Seu boleto é [link] e sua senha provisória é [senha]."

    FLUXO DE CLIENTE EXISTENTE:
    1. O cliente diz que já tem cadastro ou pede suporte.
    2. Você pede o e-mail: "Por favor, informe seu e-mail de cadastro."
    3. Você CHAMA `check_client_status(email)`.
    4. Com base no retorno, você informa o plano atual ou faturas pendentes.

    REGRAS CRÍTICAS:
    - **NUNCA PEÇA ID DE CLIENTE**: Você não precisa de autenticação prévia. O e-mail é sua chave de busca.
    - **NUNCA SIMULE CADASTRO**: Não diga "criei um ticket" ou "já está valendo" sem chamar `create_subscription`.
    - **DADOS COMPLETOS**: Para `create_subscription`, você PRECISA de Nome, Email, CPF, Endereço e Plano. Se faltar algo, pergunte.
    - **ALUCINAÇÃO ZERO**: Se `list_plans` retornar apenas "Plano A", você só vende "Plano A".
    """

    def __init__(self):
        self.kernel = Kernel()
        
        self.is_configured = False
        if not settings.AZURE_OPENAI_ENDPOINT or not settings.AZURE_OPENAI_KEY:
            logger.error("Azure OpenAI credentials not found in General Agent.")
        else:
            try:
                self.kernel.add_service(
                    AzureChatCompletion(
                        service_id="general",
                        deployment_name=settings.AZURE_OPENAI_DEPLOYMENT_GPT4O_MINI,
                        endpoint=settings.AZURE_OPENAI_ENDPOINT,
                        api_key=settings.AZURE_OPENAI_KEY,
                        api_version=settings.AZURE_OPENAI_API_VERSION
                    )
                )
                self.is_configured = True
            except Exception as e:
                logger.error(f"Failed to initialize AzureChatCompletion in General Agent: {e}")
        
        self.kernel.add_plugin(GeneralPlugin(), plugin_name="GeneralPlugin")
        
        logger.info("General Agent initialized")

    async def process_message(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Process a message using the agent.
        """
        chat_history = ChatHistory()
        chat_history.add_system_message(self.SYSTEM_PROMPT)
        
        if context:
            # Add structured history if available
            history_list = context.get("chat_history", [])
            for msg in history_list:
                role = msg.get("role")
                content = msg.get("content")
                if role == "user":
                    chat_history.add_user_message(content)
                elif role == "assistant":
                    chat_history.add_assistant_message(content)
            
            # Add other context info as system message
            other_context = {k: v for k, v in context.items() if k != "chat_history"}
            if other_context:
                chat_history.add_system_message(f"Contexto do Cliente: {json.dumps(other_context, default=str)}")

        chat_history.add_user_message(message)
        
        if not self.is_configured:
            return "Erro de Configuração: As credenciais do Azure OpenAI não foram detectadas. Por favor, configure AZURE_OPENAI_KEY e AZURE_OPENAI_ENDPOINT nas configurações do App Service."

        try:
            chat_service = self.kernel.get_service(service_id="general")
        except Exception as e:
            logger.error(f"Failed to get chat service: {e}")
            return f"Desculpe, estou com problemas técnicos no momento. Detalhe: {str(e)}"
        
        from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
        from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
        
        execution_settings = AzureChatPromptExecutionSettings(
            temperature=0.2, # Lower temperature for even stricter adherence
            function_choice_behavior=FunctionChoiceBehavior.Auto()
        )
        
        try:
            result = await chat_service.get_chat_message_content(
                chat_history=chat_history,
                settings=execution_settings,
                kernel=self.kernel
            )
            return str(result)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"Ocorreu um erro técnico detalhado: {str(e)}"
