import json
import logging
from typing import Dict, Optional

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import kernel_function

from src.config.settings import settings
from src.services.sales_service import SalesService

logger = logging.getLogger(__name__)

class SalesPlugin:
    """Plugin for sales and plan management."""
    
    @kernel_function(description="Obtém o perfil e uso atual do cliente.")
    def get_customer_profile(self, cliente_id: int) -> str:
        """
        Retorna perfil.
        Args:
            cliente_id: ID do cliente.
        """
        profile = SalesService.get_customer_profile(cliente_id)
        return json.dumps(profile)

    @kernel_function(description="Recomenda planos baseados no perfil de uso do cliente.")
    def get_plan_recommendations(self, cliente_id: int) -> str:
        """
        Retorna recomendações.
        Args:
            cliente_id: ID do cliente.
        """
        recs = SalesService.get_plan_recommendations(cliente_id)
        if not recs:
            return "O plano atual do cliente já parece adequado ao seu uso."
        return json.dumps(recs)

    @kernel_function(description="Calcula a diferença de valor entre planos.")
    def calculate_upgrade_cost(self, current_plan_name: str, new_plan_name: str) -> str:
        """
        Calcula custo.
        Args:
            current_plan_name: Nome do plano atual.
            new_plan_name: Nome do novo plano desejado.
        """
        return SalesService.calculate_upgrade_cost(current_plan_name, new_plan_name)

class SalesAgent:
    """
    Agent specialized in sales and upgrades.
    """
    
    SYSTEM_PROMPT = """Você é o Agente de Vendas da Central de Atendimento.
    Sua meta é ajudar o cliente a encontrar o melhor plano, focando em suas necessidades reais.
    
    FERRAMENTAS:
    1. get_customer_profile: Use para entender o que o cliente tem hoje e como usa.
    2. get_plan_recommendations: Use para ver sugestões baseadas em dados.
    3. calculate_upgrade_cost: Use quando o cliente perguntar sobre preços de mudança.
    
    REGRAS:
    - Pratique Venda Consultiva: Não empurre o plano mais caro. Sugira o que faz sentido.
    - Se o cliente quiser cancelar (downgrade), tente entender o motivo e ofereça alternativas, mas seja respeitoso.
    - Destaque os benefícios (ex: WiFi Mesh, Streaming incluso) ao justificar o preço.
    """

    def __init__(self):
        self.kernel = Kernel()
        
        if settings.AZURE_OPENAI_KEY and settings.AZURE_OPENAI_ENDPOINT:
            self.kernel.add_service(
                AzureChatCompletion(
                    service_id="sales",
                    deployment_name=settings.AZURE_OPENAI_DEPLOYMENT_GPT4O_MINI,
                    endpoint=settings.AZURE_OPENAI_ENDPOINT,
                    api_key=settings.AZURE_OPENAI_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION
                )
            )
        else:
            logger.warning("Azure OpenAI credentials not found. Sales Agent will not work correctly.")
        
        self.kernel.add_plugin(SalesPlugin(), plugin_name="SalesPlugin")
        
        logger.info("Sales Agent initialized")

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
            chat_service = self.kernel.get_service(service_id="sales")
        except Exception as e:
            logger.error(f"Failed to get chat service: {e}")
            return "Desculpe, estou com problemas técnicos no momento."
        
        from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
        from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
        
        execution_settings = AzureChatPromptExecutionSettings(
            temperature=0.4, # Slightly higher creativity for sales
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
