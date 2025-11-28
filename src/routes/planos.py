from fastapi import APIRouter, Depends, HTTPException
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

@router.get("/{plano_id}")
async def obter_plano(plano_id: int, db: AsyncSession = Depends(get_db)):
    """Retorna os detalhes de um plano específico."""
    result = await db.execute(select(Plano).filter(Plano.plano_id == plano_id))
    plano = result.scalars().first()
    
    if not plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    return plano
