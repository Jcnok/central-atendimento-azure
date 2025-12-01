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

    @kernel_function(description="Busca tickets abertos do cliente atual.")
    async def get_open_tickets(self) -> str:
        """
        Busca tickets abertos.
        """
        if not self.current_client_id:
            return "Erro: Cliente não identificado no contexto."
            
        tickets = await TechnicalService.get_open_tickets(self.current_client_id)
        if tickets:
            return json.dumps(tickets)
        return "O cliente não possui tickets abertos no momento."

    @kernel_function(description="Atualiza um ticket existente (status, prioridade ou nota).")
    async def update_ticket(self, ticket_id: int, status: Optional[str] = None, priority: Optional[str] = None, note: Optional[str] = None) -> str:
        """
        Atualiza ticket.
        Args:
            ticket_id: ID do ticket.
            status: Novo status (ex: resolvido).
            priority: Nova prioridade (ex: alta).
            note: Nota ou observação a adicionar.
        """
        result = await TechnicalService.update_ticket(ticket_id, status, priority, note)
        return json.dumps(result)

class TechnicalAgent:
    """
    Agent specialized in technical support.
    """
    
    SYSTEM_PROMPT = """Você é o Agente Técnico da Central de Atendimento.
    Sua missão é ajudar clientes a resolver problemas técnicos de internet, TV e telefone.
    
    FERRAMENTAS DISPONÍVEIS:
    1. search_knowledge_base: Use para buscar soluções conhecidas.
    2. check_system_status: Use se o cliente relatar queda geral.
    3. get_open_tickets: Use SEMPRE no início do atendimento para saber se já existe chamado aberto.
    4. create_ticket: Use APENAS se não houver ticket aberto e não conseguir resolver com a base de conhecimento.
    5. update_ticket: Use para modificar um ticket existente (resolver, escalar, adicionar nota).
    6. identify_client: Use para encontrar o cadastro do cliente pelo EMAIL.
    
    REGRAS DE FLUXO:
    1. **Identificação**: Se não tiver o ID do cliente, peça o email e use `identify_client`.
    2. **Verificação Inicial**: Assim que identificar o cliente, use `get_open_tickets` para ver se ele já tem pendências.
    
    CENÁRIOS DE TICKET:
    - **Cenário A (Internet Voltou)**: Se o cliente informar que o serviço voltou e houver ticket aberto, use `update_ticket` com `status='resolvido'` e `note='Cliente confirmou normalização'`.
    - **Cenário B (Recusa de Testes)**: Se o cliente se recusar a fazer testes, use `update_ticket` no ticket existente (ou crie um novo) com `priority='alta'` e `note='Cliente recusou procedimentos técnicos'`.
    - **Cenário C (Problema Persiste)**: Se os procedimentos da base de conhecimento não funcionarem, crie um ticket (`create_ticket`) ou atualize o existente com nota técnica.
    
    DIRETRIZES:
    - NUNCA crie um novo ticket se já existir um aberto para o mesmo problema. Atualize o existente.
    - Seja direto e resolutivo.
    """

    def __init__(self):
        self.kernel = Kernel()
        self.plugin = TechnicalPlugin() # Keep reference to plugin instance
        
        self.is_configured = False
        if not settings.AZURE_OPENAI_ENDPOINT or not settings.AZURE_OPENAI_KEY:
            logger.error("Azure OpenAI credentials not found in Technical Agent.")
        else:
            try:
                self.kernel.add_service(
                    AzureChatCompletion(
                        service_id="technical",
                        deployment_name=settings.AZURE_OPENAI_DEPLOYMENT_GPT4O_MINI,
                        endpoint=settings.AZURE_OPENAI_ENDPOINT,
                        api_key=settings.AZURE_OPENAI_KEY,
                        api_version=settings.AZURE_OPENAI_API_VERSION
                    )
                )
                self.is_configured = True
            except Exception as e:
                logger.error(f"Failed to initialize AzureChatCompletion in Technical Agent: {e}")
        
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
        
        if not self.is_configured:
            return "Erro de Configuração: As credenciais do Azure OpenAI não foram detectadas. Por favor, configure AZURE_OPENAI_KEY e AZURE_OPENAI_ENDPOINT nas configurações do App Service."

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
