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
    
    @kernel_function(description="Gera uma segunda via de boleto para pagamento.")
    def generate_boleto(self, email: str, cpf: Optional[str] = None) -> str:
        """
        Gera um boleto.
        Args:
            email: Email do cliente.
            cpf: CPF do cliente (opcional).
        """
        result = FinancialService.gerar_boleto_simulado(email, cpf)
        if result:
            return json.dumps(result)
        return "Não foi possível encontrar boletos pendentes para este email."

    @kernel_function(description="Verifica o status de pagamento de um boleto.")
    def check_payment_status(self, boleto_id: str) -> str:
        """
        Verifica status.
        Args:
            boleto_id: Código do boleto ou ID da fatura.
        """
        status = FinancialService.check_payment_status(boleto_id)
        return f"O status do boleto {boleto_id} é: {status}"

    @kernel_function(description="Lista as faturas recentes do cliente.")
    def get_invoices(self, cliente_id: int) -> str:
        """
        Lista faturas.
        Args:
            cliente_id: ID do cliente.
        """
        invoices = FinancialService.get_invoices(cliente_id)
        return json.dumps(invoices)

class FinancialAgent:
    """
    Agent specialized in financial matters.
    """
    
    SYSTEM_PROMPT = """Você é o Agente Financeiro da Central de Atendimento.
    Sua responsabilidade é ajudar os clientes com questões financeiras como boletos, faturas e pagamentos.
    
    Você tem acesso a ferramentas para:
    1. Gerar 2ª via de boleto (generate_boleto)
    2. Verificar status de pagamento (check_payment_status)
    3. Listar faturas (get_invoices)
    
    REGRAS:
    - Sempre seja educado e profissional.
    - Antes de gerar um boleto, confirme o email do cliente se não estiver no contexto.
    - Se a ferramenta retornar um erro ou não encontrar dados, explique claramente ao cliente.
    - Não invente dados financeiros. Use apenas o que as ferramentas retornarem.
    """

    def __init__(self):
        self.kernel = Kernel()
        
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
        self.kernel.add_plugin(FinancialPlugin(), plugin_name="FinancialPlugin")
        
        logger.info("Financial Agent initialized")

    async def process_message(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Process a message using the agent.
        """
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
