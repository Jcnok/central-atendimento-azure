from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date, timedelta
import random

from src.config.database import get_db
from src.utils.security import get_current_user
from src.models.fatura import Fatura
from src.models.pagamento import Pagamento
from src.models.cliente import Cliente

router = APIRouter(prefix="/financeiro", tags=["Financeiro"])

@router.get("/faturas/{cliente_id}")
async def listar_faturas_cliente(
    cliente_id: int, 
    status: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lista todas as faturas de um cliente."""
    from src.models.contrato import Contrato
    
    # Get contracts for client
    result = await db.execute(select(Contrato).filter(Contrato.cliente_id == cliente_id))
    contratos = result.scalars().all()
    contrato_ids = [c.contrato_id for c in contratos]
    
    if not contrato_ids:
        return []
        
    query = select(Fatura).filter(Fatura.contrato_id.in_(contrato_ids))
    
    if status:
        query = query.filter(Fatura.status == status)
        
    query = query.order_by(Fatura.data_vencimento.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/fatura/{cliente_id}")
async def obter_ultima_fatura(
    cliente_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtém a última fatura de um cliente."""
    from src.models.contrato import Contrato
    
    result = await db.execute(select(Contrato).filter(Contrato.cliente_id == cliente_id))
    contratos = result.scalars().all()
    contrato_ids = [c.contrato_id for c in contratos]
    
    if not contrato_ids:
        raise HTTPException(status_code=404, detail="Cliente sem contratos")
        
    result = await db.execute(
        select(Fatura)
        .filter(Fatura.contrato_id.in_(contrato_ids))
        .order_by(Fatura.data_vencimento.desc())
    )
    fatura = result.scalars().first()
    
    if not fatura:
        raise HTTPException(status_code=404, detail="Nenhuma fatura encontrada")
        
    return fatura

@router.post("/pagamentos/")
async def registrar_pagamento(
    fatura_id: int, 
    valor_pago: float, 
    forma_pagamento: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Registra o pagamento de uma fatura."""
    result = await db.execute(select(Fatura).filter(Fatura.fatura_id == fatura_id))
    fatura = result.scalars().first()
    
    if not fatura:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
        
    if fatura.status == "pago":
        raise HTTPException(status_code=400, detail="Fatura já paga")
        
    pagamento = Pagamento(
        fatura_id=fatura_id,
        data_pagamento=date.today(),
        valor_pago=valor_pago,
        forma_pagamento=forma_pagamento
    )
    
    fatura.status = "pago"
    
    db.add(pagamento)
    await db.commit()
    await db.refresh(pagamento)
    return pagamento

@router.post("/gerar-boleto/{cliente_id}")
async def gerar_boleto_cliente(
    cliente_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Gera um boleto para a última fatura em aberto do cliente."""
    from src.models.contrato import Contrato
    
    result = await db.execute(select(Contrato).filter(Contrato.cliente_id == cliente_id))
    contratos = result.scalars().all()
    contrato_ids = [c.contrato_id for c in contratos]
    
    if not contrato_ids:
        raise HTTPException(status_code=404, detail="Cliente sem contratos")
        
    result = await db.execute(
        select(Fatura)
        .filter(Fatura.contrato_id.in_(contrato_ids), Fatura.status != "pago")
        .order_by(Fatura.data_vencimento.desc())
    )
    fatura = result.scalars().first()
    
    if not fatura:
        raise HTTPException(status_code=404, detail="Nenhuma fatura em aberto encontrada")
        
    # Generate mock boleto data
    boleto_cod = f"34191.{random.randint(10000, 99999)} {random.randint(10000, 99999)}.{random.randint(100000, 999999)} {random.randint(1, 9)} {random.randint(10000000000000, 99999999999999)}"
    
    return {
        "boleto_cod": boleto_cod,
        "vencimento": fatura.data_vencimento,
        "valor": fatura.valor
    }
