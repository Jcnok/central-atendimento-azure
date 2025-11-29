from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import get_db
from src.utils.security import get_current_user
from src.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

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
