from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Optional, Any
import logging

from src.agents.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    agent_used: str
    confidence: float
    routing_reasoning: Optional[str] = None

# Dependency to get orchestrator (could be singleton)
def get_orchestrator():
    return AgentOrchestrator()

from src.utils.security import get_optional_current_client
from src.models.cliente import Cliente

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
    client: Optional[Cliente] = Depends(get_optional_current_client)
):
    """
    Process a chat message through the Agent Orchestrator.
    """
    try:
        # Prepare context
        context = request.context or {}
        context["session_id"] = request.session_id
        
        if client:
            context["client_id"] = client.id
            context["client_name"] = client.nome
            context["client_email"] = client.email
        
        # Process
        result = await orchestrator.process_message(request.message, context)
        
        return ChatResponse(
            response=result.get("response", "Erro ao processar resposta."),
            agent_used=result.get("agent_used", "unknown"),
            confidence=result.get("confidence", 0.0),
            routing_reasoning=result.get("routing_reasoning")
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
