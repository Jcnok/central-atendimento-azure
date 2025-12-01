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

    @kernel_function(description="Aplica desconto de retenção (20% por 6 meses).")
    async def apply_discount(self, cliente_id: int) -> str:
        """
        Aplica desconto.
        Args:
            cliente_id: ID do cliente.
        """
        return json.dumps(await SalesService.apply_discount(cliente_id))

    @kernel_function(description="Cria um ticket manual para vendas ou financeiro.")
    async def create_ticket(self, description: str, priority: str = "normal") -> str:
        """
        Cria ticket.
        Args:
            description: Descrição.
            priority: Prioridade.
        """
        # Precisamos do cliente_id do contexto, mas o plugin não tem acesso direto ao self.agent
        # Vamos assumir que o contexto foi injetado ou passar como argumento se mudarmos a arquitetura
        # Por simplificação, vamos usar um método que o agente chama injetando o ID, 
        # mas como kernel_function é stateless, precisamos de um jeito de passar o ID.
        # O SalesPlugin atual não tem estado do cliente_id como o TechnicalPlugin.
        # Vamos adicionar o estado.
        pass 

    # CORREÇÃO: O SalesPlugin precisa de estado para o cliente_id igual ao TechnicalPlugin
    def __init__(self):
        self.current_client_id = None

    def set_context(self, client_id: int):
        self.current_client_id = client_id

    @kernel_function(description="Cria um ticket manual para vendas ou financeiro.")
    async def create_ticket(self, description: str, priority: str = "normal") -> str:
        if not self.current_client_id:
            return "Erro: Cliente não identificado."
        return json.dumps(await SalesService.create_ticket(self.current_client_id, description, priority))

class SalesAgent:
    """
    Agent specialized in sales and upgrades.
    """
    
    SYSTEM_PROMPT = """Você é o Agente de Vendas da Central de Atendimento.
    Sua personalidade é PROATIVA, PERSUASIVA e FOCADA EM RESULTADOS (estilo "Lobo de Wall Street", mas polido e profissional).
    
    FERRAMENTAS:
    1. get_customer_profile: Use para entender o plano atual.
    2. get_plan_recommendations: Sugestões de planos.
    3. calculate_upgrade_cost: Comparar preços.
    4. upgrade_plan: EFETIVAR a mudança de plano.
    5. apply_discount: ÚLTIMO RECURSO para retenção (20% off por 6 meses).
    6. create_ticket: Para casos que precisem de análise humana.
    
    ESTRATÉGIA DE UPGRADE (Se o cliente demonstrar interesse):
    1.  **Oferta Direta**: Não pergunte "se" ele quer ver. Diga "Tenho o plano perfeito para você: [Nome do Plano]".
    2.  **Benefícios Imediatos**:
        -   **Internet**: "A atualização ocorre em no máximo 2 horas. Sem troca de equipamento, tudo remoto."
        -   **TV**: "Desbloqueio automático em até 4 horas. Você recebe o contrato por email."
    3.  **Fechamento**: "Posso confirmar a atualização agora e já liberar a nova velocidade?"
    
    ESTRATÉGIA DE RETENÇÃO (Se o cliente quiser cancelar/downgrade):
    1.  **Empatia e Sondagem**: "Entendo que imprevistos acontecem. O que houve? Preço ou qualidade?"
    2.  **Valorização**: Mostre o que ele perde se sair (ex: benefícios do plano atual).
    3.  **Cartada Final (Desconto)**: Se ele insistir em cancelar, ofereça: "Para mantermos nossa parceria, consigo liberar AGORA um desconto de 20% nas próximas 6 mensalidades. O que acha?"
    4.  **Ação**: Se aceitar, use `apply_discount`.
    
    REGRAS GERAIS:
    - Se o cliente aceitar o upgrade, use `upgrade_plan` IMEDIATAMENTE.
    - Se houver erro técnico no upgrade, use `create_ticket` e informe o protocolo.
    - Seja objetivo. Não use textos longos e genéricos.
    """

    def __init__(self):
        self.kernel = Kernel()
        
        self.is_configured = False
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
                self.is_configured = True
            except Exception as e:
                logger.error(f"Failed to initialize AzureChatCompletion in Sales Agent: {e}")
        
        self.plugin = SalesPlugin()
        self.kernel.add_plugin(self.plugin, plugin_name="SalesPlugin")
        
        logger.info("Sales Agent initialized")

    async def process_message(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Process a message using the agent.
        """
        chat_history = ChatHistory()
        chat_history.add_system_message(self.SYSTEM_PROMPT)
        
        if context and "client_id" in context:
            self.plugin.set_context(context["client_id"])
            
        if context:
             chat_history.add_system_message(f"Contexto do Cliente: {json.dumps(context, default=str)}")

        chat_history.add_user_message(message)
        
        if not self.is_configured:
            return "Erro de Configuração: As credenciais do Azure OpenAI não foram detectadas. Por favor, configure AZURE_OPENAI_KEY e AZURE_OPENAI_ENDPOINT nas configurações do App Service."

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
