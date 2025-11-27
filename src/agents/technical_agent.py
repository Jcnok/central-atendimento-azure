import json
import logging
from typing import Dict, Optional

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import kernel_function

from src.config.settings import settings
from src.services.technical_service import TechnicalService

logger = logging.getLogger(__name__)

class TechnicalPlugin:
    """Plugin for technical support operations."""
    
    @kernel_function(description="Busca soluções na base de conhecimento técnica.")
    def search_knowledge_base(self, query: str) -> str:
        """
        Busca na base de conhecimento.
        Args:
            query: O termo de busca ou descrição do problema.
        """
        results = TechnicalService.search_knowledge_base(query)
        if results:
            return json.dumps(results)
        return "Não encontrei informações específicas sobre isso na minha base de conhecimento."

    @kernel_function(description="Cria um ticket de suporte técnico para o cliente.")
    def create_ticket(self, description: str, priority: str = "normal") -> str:
        """
        Cria um ticket.
        Args:
            description: Descrição detalhada do problema.
            priority: Prioridade (baixa, normal, alta).
        """
        result = TechnicalService.create_ticket(description, priority)
        return json.dumps(result)

    @kernel_function(description="Verifica o status operacional dos sistemas e serviços.")
    def check_system_status(self) -> str:
        """
        Verifica status do sistema.
        """
        status = TechnicalService.check_system_status()
        return json.dumps(status)

class TechnicalAgent:
    """
    Agent specialized in technical support.
    """
    
    SYSTEM_PROMPT = """Você é o Agente Técnico da Central de Atendimento.
    Sua missão é ajudar clientes a resolver problemas técnicos de internet, TV e telefone.
    
    FERRAMENTAS DISPONÍVEIS:
    1. search_knowledge_base: Use para buscar soluções conhecidas antes de criar um ticket.
    2. check_system_status: Use se o cliente relatar queda geral ou falha massiva.
    3. create_ticket: Use APENAS se não conseguir resolver o problema com a base de conhecimento.
    
    REGRAS:
    - Primeiro, tente diagnosticar e resolver o problema usando a base de conhecimento.
    - Se encontrar uma solução, explique o passo a passo para o cliente.
    - Se o cliente confirmar que não resolveu, aí sim crie um ticket.
    - Seja empático e técnico, mas use linguagem acessível.
    """

    def __init__(self):
        self.kernel = Kernel()
        
        if settings.AZURE_OPENAI_KEY and settings.AZURE_OPENAI_ENDPOINT:
            self.kernel.add_service(
                AzureChatCompletion(
                    service_id="technical",
                    deployment_name=settings.AZURE_OPENAI_DEPLOYMENT_GPT4O_MINI,
                    endpoint=settings.AZURE_OPENAI_ENDPOINT,
                    api_key=settings.AZURE_OPENAI_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION
                )
            )
        else:
            logger.warning("Azure OpenAI credentials not found. Technical Agent will not work correctly.")
        
        self.kernel.add_plugin(TechnicalPlugin(), plugin_name="TechnicalPlugin")
        
        logger.info("Technical Agent initialized")

    async def process_message(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Process a message using the agent.
        """
        chat_history = ChatHistory()
        chat_history.add_system_message(self.SYSTEM_PROMPT)
        
        if context:
             chat_history.add_system_message(f"Contexto do Cliente: {json.dumps(context, default=str)}")

        chat_history.add_user_message(message)
        
        try:
            chat_service = self.kernel.get_service(service_id="technical")
        except Exception as e:
            logger.error(f"Failed to get chat service: {e}")
            return "Desculpe, estou com problemas técnicos no momento."
        
        from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
        from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
        
        execution_settings = AzureChatPromptExecutionSettings(
            temperature=0.3,
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
            return "Ocorreu um erro ao processar sua solicitação."
