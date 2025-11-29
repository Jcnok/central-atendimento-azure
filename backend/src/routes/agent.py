from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.config.database import get_db
from src.utils.security import get_current_user
from src.agents.sql_agent import SQLAgent

router = APIRouter(prefix="/agent", tags=["Agent"])

class AgentQuery(BaseModel):
    query: str

@router.post("/")
async def ask_agent(
    request: AgentQuery,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    """
    Endpoint para consultar o Agente CRM (SQL).
    O agente traduz perguntas em linguagem natural para SQL e retorna os resultados.
    """
    agent = SQLAgent(db)
    response = await agent.process_query(request.query)
    return {"response": response}
