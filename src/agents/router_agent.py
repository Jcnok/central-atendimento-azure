"""
Router Agent - Intelligent Intent Classification
Classifies incoming messages and routes to specialized agents
"""
import json
import logging
from typing import Dict, Optional

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory
from semantic_kernel.prompt_template import PromptTemplateConfig

from src.config.settings import settings

logger = logging.getLogger(__name__)


class RouterAgent:
    """
    Router Agent that classifies user intent and routes to appropriate specialized agent.
    Uses GPT-4o-mini for cost-effective classification.
    """
    
    AVAILABLE_AGENTS = {
        "financial_agent": "Boletos, pagamentos, faturas, cobranças, parcelamentos",
        "technical_agent": "Problemas técnicos, bugs, erros de sistema, suporte",
        "sales_agent": "Upgrades, downgrades, novos planos, cancelamentos, comercial",
        "general_agent": "Dúvidas gerais, agradecimentos, saudações, FAQ"
    }
    
    SYSTEM_PROMPT = """Você é o Router Agent da Central de Atendimento. Sua única função é classificar a intenção do cliente e direcioná-lo ao agente especializado correto.

AGENTES DISPONÍVEIS:
- financial_agent: Boletos, pagamentos, faturas, cobranças, parcelamentos
- technical_agent: Problemas técnicos, bugs, erros de sistema, suporte
- sales_agent: Upgrades, downgrades, novos planos, cancelamentos, comercial
- general_agent: Dúvidas gerais, agradecimentos, saudações, FAQ

REGRAS:
1. Analise APENAS a intenção principal da mensagem
2. Em caso de dúvida, use general_agent
3. Retorne APENAS um objeto JSON válido no formato: {"agent": "nome_do_agente", "confidence": 0.95, "reasoning": "breve explicação"}
4. O campo confidence deve ser um número entre 0 e 1
5. Seja preciso e rápido na classificação"""

    def __init__(self):
        """Initialize Router Agent with Azure OpenAI connection"""
        self.kernel = Kernel()
        
        # Add Azure OpenAI service
        self.kernel.add_service(
            AzureChatCompletion(
                service_id="router",
                deployment_name=settings.AZURE_OPENAI_DEPLOYMENT_GPT4O_MINI,
                endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION
            )
        )
        
        logger.info("Router Agent initialized successfully")
    
    async def route(self, message: str, context: Optional[Dict] = None) -> Dict[str, any]:
        """
        Route a message to the appropriate agent
        
        Args:
            message: User message to classify
            context: Optional context (cliente_id, previous messages, etc.)
        
        Returns:
            Dict with agent name, confidence, and reasoning
        """
        try:
            # Build prompt with context if available
            user_prompt = f"Mensagem do cliente: {message}"
            if context:
                user_prompt += f"\n\nContexto adicional: {json.dumps(context, ensure_ascii=False)}"
            
            # Create chat history
            chat_history = ChatHistory()
            chat_history.add_system_message(self.SYSTEM_PROMPT)
            chat_history.add_user_message(user_prompt)
            
            # Get classification from LLM using service directly
            chat_service = self.kernel.get_service(service_id="router")
            
            # Create execution settings
            from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
            settings = AzureChatPromptExecutionSettings(
                temperature=0.3,  # Low temperature for consistent classification
                max_tokens=150
            )
            
            response = await chat_service.get_chat_message_content(
                chat_history=chat_history,
                settings=settings
            )
            
            # Parse JSON response
            result = json.loads(str(response))
            
            # Validate agent name
            if result["agent"] not in self.AVAILABLE_AGENTS:
                logger.warning(f"Invalid agent returned: {result['agent']}, defaulting to general_agent")
                result["agent"] = "general_agent"
                result["confidence"] = 0.5
            
            logger.info(f"Routed to {result['agent']} with confidence {result['confidence']}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return {
                "agent": "general_agent",
                "confidence": 0.0,
                "reasoning": "Erro na classificação, usando agente geral"
            }
        except Exception as e:
            logger.error(f"Error in routing: {e}")
            return {
                "agent": "general_agent",
                "confidence": 0.0,
                "reasoning": f"Erro: {str(e)}"
            }
    
    async def get_agent_info(self, agent_name: str) -> Optional[str]:
        """Get description of a specific agent"""
        return self.AVAILABLE_AGENTS.get(agent_name)
    
    def list_agents(self) -> Dict[str, str]:
        """List all available agents and their capabilities"""
        return self.AVAILABLE_AGENTS.copy()
