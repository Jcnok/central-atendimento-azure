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
    """Plugin for general inquiries."""
    
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

class GeneralAgent:
    """
    Agent specialized in general inquiries.
    """
    
    SYSTEM_PROMPT = """Você é o Agente Geral da Central de Atendimento.
    Sua função é responder dúvidas simples, institucionais e direcionar o cliente.
    
    FERRAMENTAS:
    1. search_faq: Use para responder perguntas comuns.
    2. get_company_info: Use para dados como endereço, telefone e horários.
    
    REGRAS:
    - Seja direto e cordial.
    - Se a pergunta for muito técnica ou financeira, sugira que o cliente fale com o especialista.
    - Mantenha um tom de voz acolhedor.
    - Se o cliente pedir algo que exija login (fatura, suporte específico) e não estiver logado, direcione-o para: [Minha Conta](/login).
    - PRIVACIDADE: NUNCA pergunte ou revele IDs internos (cliente_id, etc). Você já tem o contexto necessário.
    - CONTEXTO: Você tem acesso ao 'client_plan' e 'client_tickets'. Use isso para responder perguntas básicas como "Qual meu plano?".
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
