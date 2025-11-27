from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.config.database import get_db
from src.models.plano import Plano

router = APIRouter(prefix="/planos", tags=["Planos"])

@router.get("/")
async def listar_planos(db: AsyncSession = Depends(get_db)):
    """Lista todos os planos disponíveis (Público)"""
    result = await db.execute(select(Plano))
    planos = result.scalars().all()
    return planos
