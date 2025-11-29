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
from src.config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
    client: Optional[Cliente] = Depends(get_optional_current_client),
    db: AsyncSession = Depends(get_db)  # Added DB dependency
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
            
            # Fetch Active Plan
            from sqlalchemy import select
            from src.models.contrato import Contrato
            from src.models.plano import Plano
            from sqlalchemy.orm import selectinload
            
            contrato_result = await db.execute(
                select(Contrato)
                .options(selectinload(Contrato.plano))
                .filter(Contrato.cliente_id == client.id, Contrato.status == 'ativo')
            )
            contrato = contrato_result.scalars().first()
            
            if contrato:
                context["client_plan"] = {
                    "name": contrato.plano.nome,
                    "speed": contrato.plano.velocidade,
                    "price": float(contrato.plano.preco)
                }
            else:
                context["client_plan"] = "Nenhum plano ativo"

            # Fetch Recent Tickets
            from src.models.chamado import Chamado
            chamados_result = await db.execute(
                select(Chamado)
                .filter(Chamado.cliente_id == client.id)
                .order_by(Chamado.data_criacao.desc())
                .limit(3)
            )
            chamados = chamados_result.scalars().all()
            context["client_tickets"] = [
                {"id": c.id, "subject": c.mensagem, "status": c.status} for c in chamados
            ]
            
            # Inject Client Summary (Plan & Recent Tickets)
            # We need a DB session here. Since we don't have one injected in the endpoint signature directly for this logic,
            # we should add it.
            # BUT, wait, we can't easily add 'db' to the signature if it wasn't there. 
            # Let's check the file content again. It DOES NOT have 'db' in signature.
            # I will add 'db: AsyncSession = Depends(get_db)' to the signature in a separate edit or assume I can add it here.
            # Actually, I'll add the db dependency to the function signature first.
            pass
        
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
