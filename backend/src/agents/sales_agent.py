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
    async def get_customer_profile(self, cliente_id: int) -> str:
        """
        Retorna perfil.
        Args:
            cliente_id: ID do cliente.
        """
        profile = await SalesService.get_customer_profile(cliente_id)
        return json.dumps(profile)

    @kernel_function(description="Recomenda planos baseados no perfil de uso do cliente.")
    async def get_plan_recommendations(self, cliente_id: int) -> str:
        """
        Retorna recomendações.
        Args:
            cliente_id: ID do cliente.
        """
        recs = await SalesService.get_plan_recommendations(cliente_id)
        return json.dumps(recs)

    @kernel_function(description="Calcula a diferença de valor entre planos.")
    async def calculate_upgrade_cost(self, current_plan_name: str, new_plan_name: str) -> str:
        """
        Calcula custo.
        Args:
            current_plan_name: Nome do plano atual.
            new_plan_name: Nome do novo plano desejado.
        """
        return await SalesService.calculate_upgrade_cost(current_plan_name, new_plan_name)

    @kernel_function(description="Realiza o upgrade do plano do cliente.")
    async def upgrade_plan(self, cliente_id: int, new_plan_name: str) -> str:
        """
        Realiza upgrade.
        Args:
            cliente_id: ID do cliente.
            new_plan_name: Nome do novo plano.
        """
        return await SalesService.upgrade_plan(cliente_id, new_plan_name)

class SalesAgent:
    """
    Agent specialized in sales and upgrades.
    """
    
    SYSTEM_PROMPT = """Você é o Agente de Vendas da Central de Atendimento.
    Sua meta é ajudar o cliente a encontrar o melhor plano e realizar upgrades.
    
    FERRAMENTAS:
    1. get_customer_profile: Use para entender o plano atual.
    2. get_plan_recommendations: Sugestões de planos.
    3. calculate_upgrade_cost: Comparar preços.
    4. upgrade_plan: EFETIVAR a mudança de plano.
    
    REGRAS CRÍTICAS DE PRIVACIDADE:
    - Você JÁ RECEBE o 'cliente_id' no contexto. NUNCA pergunte o ID ao cliente.
    - O contexto também contém 'client_plan' (Plano Atual) e 'client_tickets' (Histórico). USE ESSAS INFORMAÇÕES.
    - Se o cliente perguntar "Qual meu plano?", responda com base no 'client_plan' do contexto.
    - NUNCA revele IDs internos (cliente_id, contrato_id) nas respostas.
    - Ao confirmar um upgrade, informe o Protocolo gerado pela ferramenta.
    
    REGRAS DE ATENDIMENTO:
    - Pratique Venda Consultiva.
    - Se o cliente confirmar explicitamente a mudança, use a ferramenta 'upgrade_plan'.
    - Seja claro sobre o novo valor e benefícios.
    - Se o cliente NÃO estiver logado (sem 'client_id'), foque em apresentar os planos disponíveis e seus benefícios gerais.
    - Para realizar upgrade ou ver ofertas personalizadas, direcione o cliente para o login: [Minha Conta](/login).
    """

    def __init__(self):
        self.kernel = Kernel()
        
        if not settings.AZURE_OPENAI_ENDPOINT or not settings.AZURE_OPENAI_KEY:
            logger.error("Azure OpenAI credentials not found in Sales Agent.")
        else:
            try:
                self.kernel.add_service(
                    AzureChatCompletion(
                        service_id="sales",
                        deployment_name=settings.AZURE_OPENAI_DEPLOYMENT_GPT4O_MINI,
                        endpoint=settings.AZURE_OPENAI_ENDPOINT,
                        api_key=settings.AZURE_OPENAI_KEY,
                        api_version=settings.AZURE_OPENAI_API_VERSION
                    )
                )
            except Exception as e:
                logger.error(f"Failed to initialize AzureChatCompletion in Sales Agent: {e}")
        
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
