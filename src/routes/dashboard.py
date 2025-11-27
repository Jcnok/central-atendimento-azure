from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.config.database import get_db
from src.utils.security import get_current_user
from src.services.dashboard_service import DashboardService
from src.agents.sql_agent import SQLAgent

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

class AgentQuery(BaseModel):
    query: str

@router.get("/kpis")
async def get_kpis(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    service = DashboardService(db)
    return await service.get_kpis()

@router.get("/tickets")
async def get_tickets(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    service = DashboardService(db)
    return await service.get_recent_tickets()

@router.post("/agent")
async def ask_crm_agent(
    request: AgentQuery,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    agent = SQLAgent(db)
    response = await agent.process_query(request.query)
    return {"response": response}
