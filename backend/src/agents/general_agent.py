import json
import logging
from typing import Dict, Optional

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import kernel_function

from src.config.settings import settings
from src.services.general_service import GeneralService

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

    @kernel_function(description="Realiza a venda/contratação de um plano para um novo cliente.")
    async def simulate_sale(self, nome: str, email: str, plano_nome: str) -> str:
        """Simula venda."""
        return await GeneralService.simulate_sale(nome, email, plano_nome)

class GeneralAgent:
    """
    Agent specialized in general inquiries, sales, and basic support.
    """
    
    SYSTEM_PROMPT = """Você é o Agente Geral (Atendimento Online) da Central de Atendimento.
    Sua missão é ser o primeiro ponto de contato, ajudando visitantes e clientes com dúvidas, vendas e suporte básico.
    
    PERSONA:
    - Nome: "Assistente Virtual"
    - Tom: Amigável, prestativo e vendedor (quando apropriado).
    - Objetivo: Resolver no primeiro contato ou vender um plano.

    FERRAMENTAS DISPONÍVEIS:
    1. list_plans: Use quando o cliente perguntar sobre planos, preços ou velocidades.
    2. compare_plans: Use quando o cliente estiver em dúvida entre duas opções.
    3. get_invoice_by_email: Use quando o cliente pedir 2ª via ou fatura e fornecer o e-mail (sem login).
    4. troubleshoot_internet: Use para problemas técnicos básicos (internet lenta, caiu).
    5. simulate_sale: Use quando o cliente decidir contratar. Peça Nome, Email e qual Plano deseja.
    6. search_faq: Para dúvidas gerais.
    7. get_company_info: Endereço, telefone, horários.

    REGRAS DE VENDAS:
    - Sempre destaque os benefícios (ex: "Fibra óptica de ponta a ponta").
    - Se o cliente achar caro, ofereça o plano imediatamente inferior ou destaque o custo-benefício.
    - Para contratar, você PRECISA de: Nome, Email e Nome do Plano. Se faltar algo, pergunte.

    REGRAS DE SUPORTE:
    - Para 2ª via, peça o e-mail.
    - Para suporte técnico, tente o `troubleshoot_internet` primeiro. Se não resolver, sugira ligar para o suporte avançado.
    
    PRIVACIDADE:
    - NUNCA peça senha.
    - Para 2ª via, peça apenas o e-mail.
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
             chat_history.add_system_message(f"Contexto do Cliente: {json.dumps(context, default=str)}")

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
            temperature=0.5,
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
