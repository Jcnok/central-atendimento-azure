import json
import logging
from typing import Dict, Optional

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import kernel_function

from src.config.settings import settings
from src.services.financial_service import FinancialService

logger = logging.getLogger(__name__)

class FinancialPlugin:
    """Plugin for financial operations."""
    
    def __init__(self):
        self.client_id: Optional[int] = None
        self.client_email: Optional[str] = None

    def set_context(self, client_id: Optional[int], client_email: Optional[str]):
        self.client_id = client_id
        self.client_email = client_email

    @kernel_function(description="Gera uma segunda via de boleto para pagamento.")
    async def generate_boleto(self, email: Optional[str] = None, cpf: Optional[str] = None) -> str:
        """
        Gera um boleto.
        Args:
            email: Email do cliente.
            cpf: CPF do cliente (opcional).
        """
        # Use context email if not provided
        target_email = email or self.client_email
        
        if not target_email:
            return "Erro: Email não fornecido e não encontrado no contexto."

        result = await FinancialService.gerar_boleto_simulado(target_email, cpf)
        if result:
            return json.dumps(result)
        return "Não foi possível encontrar boletos pendentes para este email."

    @kernel_function(description="Verifica o status de pagamento de um boleto.")
    async def check_payment_status(self, boleto_id: str) -> str:
        """
        Verifica status.
        Args:
            boleto_id: Código do boleto ou ID da fatura.
        """
        status = await FinancialService.check_payment_status(boleto_id)
        return f"O status do boleto {boleto_id} é: {status}"

    @kernel_function(description="Lista as faturas recentes do cliente.")
    async def get_invoices(self, cliente_id: Optional[int] = None) -> str:
        """
        Lista faturas.
        Args:
            cliente_id: ID do cliente.
        """
        # Use context ID if not provided
        target_id = cliente_id or self.client_id
        
        if not target_id:
            return "STATUS: USUÁRIO NÃO LOGADO. Não é possível listar faturas. AÇÃO NECESSÁRIA: Peça o EMAIL do cliente para verificar o cadastro usando a ferramenta 'verify_client_status'."

        invoices = await FinancialService.get_invoices(target_id)
        return json.dumps(invoices)

    @kernel_function(description="Verifica se o cliente possui cadastro pelo email.")
    async def verify_client_status(self, email: str) -> str:
        """
        Verifica cadastro.
        Args:
            email: Email do cliente.
        """
        # Reuse logic from TechnicalService or implement similar here
        # For simplicity, we can query the DB directly or use a shared service
        from src.services.technical_service import TechnicalService
        client_id = await TechnicalService.get_client_by_email(email)
        
        if client_id:
            return "Cliente encontrado. Cadastro ativo."
        return "Cliente não encontrado."

class FinancialAgent:
    """
    Agent specialized in financial matters.
    """
    
    SYSTEM_PROMPT = """Você é o Agente Financeiro da Central de Atendimento.
    Sua responsabilidade é ajudar os clientes com questões financeiras como boletos, faturas e pagamentos.
    
    FERRAMENTAS DISPONÍVEIS:
    1. generate_boleto: Gera 2ª via de boleto (Requer email).
    2. check_payment_status: Verifica status de pagamento.
    3. get_invoices: Lista faturas (Requer login/ID).
    4. verify_client_status: Verifica se o email possui cadastro.
    
    REGRAS DE OURO (Prioridade Máxima):
    1. VERIFIQUE O CONTEXTO: Antes de qualquer ação, veja se 'client_id' ou 'is_authenticated' existe no contexto.
    2. USUÁRIO ANÔNIMO (Sem 'client_id'):
       - Se pedir fatura, boleto ou dados financeiros: NÃO tente usar 'get_invoices'.
       - Responda: "Para acessar sua fatura, preciso verificar seu cadastro. Qual é o seu email?"
       - Quando o usuário fornecer o email, use 'verify_client_status'.
       - Se 'verify_client_status' confirmar o cadastro: "Encontrei seu cadastro! Por questões de segurança, acesse sua fatura fazendo login em: [Minha Conta](/login)."
       - Se não encontrar: "Não localizei cadastro com este email. Gostaria de ver nossos planos?"
    3. USUÁRIO LOGADO (Com 'client_id'):
       - Pode usar 'get_invoices' e 'generate_boleto' livremente.
    
    4. NUNCA peça CPF ou ID do cliente. Apenas Email.
    5. Se uma ferramenta retornar "USUÁRIO NÃO LOGADO", siga a regra 2 imediatamente.
    
    CONTEXTO: Você tem acesso ao 'client_id' e 'client_email' (se logado).
    """

    def __init__(self):
        self.kernel = Kernel()
        self.plugin = FinancialPlugin() # Keep reference
        
        # Add Azure OpenAI Service
        # Note: In a real scenario, we should handle cases where keys are missing
        if settings.AZURE_OPENAI_KEY and settings.AZURE_OPENAI_ENDPOINT:
            self.kernel.add_service(
                AzureChatCompletion(
                    service_id="financial",
                    deployment_name=settings.AZURE_OPENAI_DEPLOYMENT_GPT4O_MINI,
                    endpoint=settings.AZURE_OPENAI_ENDPOINT,
                    api_key=settings.AZURE_OPENAI_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION
                )
            )
        else:
            logger.warning("Azure OpenAI credentials not found. Financial Agent will not work correctly.")
        
        # Register Plugin
        self.kernel.add_plugin(self.plugin, plugin_name="FinancialPlugin")
        
        logger.info("Financial Agent initialized")

    async def process_message(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Process a message using the agent.
        """
        # Inject context into plugin
        if context:
            self.plugin.set_context(
                client_id=context.get("client_id"),
                client_email=context.get("client_email")
            )

        chat_history = ChatHistory()
        chat_history.add_system_message(self.SYSTEM_PROMPT)
        
        # Add context if relevant (e.g. customer info)
        if context:
             chat_history.add_system_message(f"Contexto do Cliente: {json.dumps(context, default=str)}")

        chat_history.add_user_message(message)
        
        try:
            chat_service = self.kernel.get_service(service_id="financial")
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
