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
    
    def __init__(self):
        self.current_client_id = None

    def set_context(self, client_id: int):
        self.current_client_id = client_id
    
    @kernel_function(description="Busca soluções na base de conhecimento técnica.")
    async def search_knowledge_base(self, query: str) -> str:
        """
        Busca na base de conhecimento.
        Args:
            query: O termo de busca ou descrição do problema.
        """
        results = await TechnicalService.search_knowledge_base(query)
        if results:
            return json.dumps(results)
        return "Não encontrei informações específicas sobre isso na minha base de conhecimento."

    @kernel_function(description="Cria um ticket de suporte técnico para o cliente.")
    async def create_ticket(self, description: str, priority: str = "normal") -> str:
        """
        Cria um ticket.
        Args:
            description: Descrição detalhada do problema.
            priority: Prioridade (baixa, normal, alta).
        """
        if not self.current_client_id:
            return "Erro: Não foi possível identificar o cliente para criar o ticket."
            
        result = await TechnicalService.create_ticket(description, priority, self.current_client_id)
        return json.dumps(result)

    @kernel_function(description="Verifica o status operacional dos sistemas e serviços.")
    async def check_system_status(self) -> str:
        """
        Verifica status do sistema.
        """
        status = await TechnicalService.check_system_status()
        return json.dumps(status)

    @kernel_function(description="Identifica o cliente pelo email para obter o ID.")
    async def identify_client(self, email: str) -> str:
        """
        Identifica cliente pelo email.
        Args:
            email: Email do cliente.
        """
        client_id = await TechnicalService.get_client_by_email(email)
        if client_id:
            self.current_client_id = client_id
            return f"Cliente identificado com sucesso. ID: {client_id}"
        return "Cliente não encontrado com este email."

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
    4. identify_client: Use para encontrar o cadastro do cliente pelo EMAIL.
    
    REGRAS:
    - Primeiro, tente diagnosticar e resolver o problema usando a base de conhecimento.
    - Se encontrar uma solução, explique o passo a passo para o cliente.
    - Se o cliente confirmar que não resolveu, aí sim crie um ticket.
    - Se precisar criar um ticket e não tiver o 'client_id' no contexto (usuário não logado), PEÇA O EMAIL e use a ferramenta 'identify_client'.
    - NUNCA peça o "ID do cliente". Peça o EMAIL.
    - Seja empático e técnico, mas use linguagem acessível.
    - CONTEXTO: Você tem acesso ao 'client_plan' (Plano Atual) e 'client_tickets' (Histórico). Verifique se o problema já foi relatado antes de abrir novo ticket.
    """

    def __init__(self):
        self.kernel = Kernel()
        self.plugin = TechnicalPlugin() # Keep reference to plugin instance
        
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
        
        self.kernel.add_plugin(self.plugin, plugin_name="TechnicalPlugin")
        
        logger.info("Technical Agent initialized")

    async def process_message(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Process a message using the agent.
        """
        # Inject context into plugin
        if context and "client_id" in context:
            self.plugin.set_context(context["client_id"])
            
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
