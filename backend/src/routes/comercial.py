from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date

from src.config.database import get_db
from src.utils.security import get_current_user
from src.models.contrato import Contrato
from src.models.plano import Plano

router = APIRouter(prefix="/comercial", tags=["Comercial"])

@router.post("/upgrade-plano/{cliente_id}")
async def upgrade_plano(
    cliente_id: int, 
    novo_plano_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Realiza o upgrade do último plano ativo para um cliente."""
    # Get active contract
    result = await db.execute(
        select(Contrato)
        .filter(Contrato.cliente_id == cliente_id, Contrato.status == 'ativo')
        .order_by(Contrato.data_inicio.desc())
    )
    contrato = result.scalars().first()
    
    if not contrato:
        raise HTTPException(status_code=404, detail="Nenhum contrato ativo encontrado")
        
    # Verify new plan
    plano_result = await db.execute(select(Plano).filter(Plano.plano_id == novo_plano_id))
    novo_plano = plano_result.scalars().first()
    
    if not novo_plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
        
    # Update contract
    contrato.plano_id = novo_plano_id
    # In a real system, we might create a new contract and close the old one, but for MVP update is fine
    
    await db.commit()
    await db.refresh(contrato)
    return {"message": f"Plano atualizado para {novo_plano.nome} com sucesso"}

@router.post("/novo-contrato/{cliente_id}")
async def novo_contrato(
    cliente_id: int, 
    plano_id: int,
    tipo_servico: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cria um novo contrato para um cliente."""
    contrato = Contrato(
        cliente_id=cliente_id,
        plano_id=plano_id,
        data_inicio=date.today(),
        status="ativo",
        tipo_servico=tipo_servico
    )
    
    db.add(contrato)
    await db.commit()
    await db.refresh(contrato)
    return contrato
