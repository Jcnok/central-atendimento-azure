import json
import logging
from typing import Dict, Optional

from src.agents.financial_agent import FinancialAgent
from src.agents.general_agent import GeneralAgent
from src.agents.router_agent import RouterAgent
from src.agents.sales_agent import SalesAgent
from src.agents.technical_agent import TechnicalAgent

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Central orchestrator that routes messages to specialized agents.
    """

    def __init__(self):
        self.router = RouterAgent()
        self.agents = {
            "financial_agent": FinancialAgent(),
            "technical_agent": TechnicalAgent(),
            "sales_agent": SalesAgent(),
            "general_agent": GeneralAgent()
        }
        logger.info("Agent Orchestrator initialized with all specialized agents")

    async def process_message(self, message: str, context: Optional[Dict] = None) -> Dict[str, any]:
        """
        Process a user message:
        1. Retrieve/Update Session Context
        2. Route to the correct agent
        3. Execute the agent
        4. Return the response
        """
        from src.memory.session_manager import SessionManager
        
        session_manager = SessionManager()
        session_id = context.get("session_id", "default") if context else "default"
        
        # 1. Retrieve Session
        session_data = session_manager.get_session(session_id) or {}
        history = session_data.get("history", [])
        
        # Append user message to history (for context window)
        history.append({"role": "user", "content": message})
        
        # Update context with history for agents
        agent_context = context.copy() if context else {}
        agent_context["chat_history"] = history[-5:] # Pass last 5 messages
        
        try:
            # Start a custom span for the transaction
            try:
                from opentelemetry import trace
                tracer = trace.get_tracer(__name__)
                span = tracer.start_span("orchestrator.process_message")
            except ImportError:
                tracer = None
                span = None

            # 2. Route
            # We pass the raw message to router, but maybe in future we pass history too
            routing_result = await self.router.route(message, agent_context)
            agent_name = routing_result.get("agent")
            confidence = routing_result.get("confidence", 0.0)
            
            if span:
                span.set_attribute("agent.name", agent_name)
                span.set_attribute("agent.confidence", confidence)
            
            logger.info(f"Orchestrator routing to {agent_name} (confidence: {confidence})")
            
            # 3. Select Agent
            agent = self.agents.get(agent_name)
            if not agent:
                logger.warning(f"Agent {agent_name} not found, falling back to general_agent")
                agent = self.agents["general_agent"]
                agent_name = "general_agent"

            # 4. Execute
            response = await agent.process_message(message, agent_context)
            
            # 5. Update Session
            history.append({"role": "assistant", "content": response, "agent": agent_name})
            session_data["history"] = history
            session_manager.save_session(session_id, session_data)
            
            if span:
                span.end()

            return {
                "response": response,
                "agent_used": agent_name,
                "confidence": confidence,
                "routing_reasoning": routing_result.get("reasoning")
            }

        except Exception as e:
            if span:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR))
                span.end()
            logger.error(f"Error in orchestrator: {e}")
            return {
                "response": "Desculpe, ocorreu um erro interno ao processar sua mensagem.",
                "agent_used": "system_error",
                "error": str(e)
            }
