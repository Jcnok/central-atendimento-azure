from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.config.database import get_db
from src.models.cliente import Cliente
from src.schemas.cliente import ClienteCreate, ClienteResponse, ClienteUpdate
from src.utils.security import get_current_user, get_current_client

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("/buscar", response_model=ClienteResponse)
async def buscar_cliente_por_email(email: str, db: AsyncSession = Depends(get_db)):
    """Busca um cliente pelo email (Público - usado no Autoatendimento)"""
    result = await db.execute(select(Cliente).filter(Cliente.email == email))
    cliente = result.scalars().first()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado"
        )
    return cliente


@router.post(
    "/",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def criar_cliente(cliente: ClienteCreate, db: AsyncSession = Depends(get_db)):
    """Cria um novo cliente"""
    try:
        from src.utils.security import get_password_hash
        
        novo_cliente = Cliente(
            nome=cliente.nome,
            email=cliente.email,
            hashed_password=get_password_hash(cliente.password),
            telefone=cliente.telefone,
            canal_preferido=cliente.canal_preferido,
        )
        db.add(novo_cliente)
        await db.commit()
        await db.refresh(novo_cliente)
        return novo_cliente
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado"
        )


@router.get(
    "/{cliente_id}",
    response_model=ClienteResponse,
    dependencies=[Depends(get_current_user)],
)
async def obter_cliente(cliente_id: int, db: AsyncSession = Depends(get_db)):
    """Obtém informações de um cliente"""
    result = await db.execute(select(Cliente).filter(Cliente.id == cliente_id))
    cliente = result.scalars().first()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado"
        )
    return cliente


@router.get(
    "/",
    response_model=list[ClienteResponse],
    dependencies=[Depends(get_current_user)],
)
async def listar_clientes(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    """Lista todos os clientes"""
    result = await db.execute(select(Cliente).offset(skip).limit(limit))
    return result.scalars().all()

@router.get(
    "/me/contratos",
    dependencies=[Depends(get_current_user)],
)
async def listar_meus_contratos(
    db: AsyncSession = Depends(get_db),
    current_client: Cliente = Depends(get_current_client)
):
    """Lista os contratos do cliente autenticado"""
    
    # Fetch contracts with Plan details
    from src.models.contrato import Contrato
    from src.models.plano import Plano
    from sqlalchemy.orm import selectinload

    query = (
        select(Contrato)
        .options(selectinload(Contrato.plano))
        .filter(Contrato.cliente_id == current_client.id)
    )
    
    result = await db.execute(query)
    contratos = result.scalars().all()
    
    # Return simplified structure
    return [
        {
            "id": c.contrato_id,
            "plan": c.plano.nome,
            "status": c.status.value if hasattr(c.status, 'value') else c.status,
            "velocidade": c.plano.velocidade,
            "preco": c.plano.preco
        }
        for c in contratos
    ]

@router.get(
    "/me/faturas",
    dependencies=[Depends(get_current_user)],
)
async def listar_minhas_faturas(
    db: AsyncSession = Depends(get_db),
    current_client: Cliente = Depends(get_current_client)
):
    """Lista as faturas do cliente autenticado"""
    
    from src.models.fatura import Fatura
    from src.models.contrato import Contrato
    
    result = await db.execute(
        select(Fatura)
        .join(Contrato)
        .filter(Contrato.cliente_id == current_client.id)
        .order_by(Fatura.data_vencimento.desc())
        .limit(5)
    )
    faturas = result.scalars().all()
    
    return [
        {
            "id": f.fatura_id,
            "valor": float(f.valor),
            "vencimento": f.data_vencimento.strftime("%d/%m/%Y"),
            "status": f.status
        }
        for f in faturas
    ]

@router.get(
    "/me/chamados",
    dependencies=[Depends(get_current_user)],
)
async def listar_meus_chamados(
    db: AsyncSession = Depends(get_db),
    current_client: Cliente = Depends(get_current_client)
):
    """Lista os chamados do cliente autenticado"""
    
    from src.models.chamado import Chamado
    
    result = await db.execute(
        select(Chamado)
        .filter(Chamado.cliente_id == current_client.id)
        .order_by(Chamado.data_criacao.desc())
        .limit(5)
    )
    chamados = result.scalars().all()
    
    return [
        {
            "id": c.id,
            "protocolo": c.protocolo,
            "assunto": c.mensagem[:30] + "..." if len(c.mensagem) > 30 else c.mensagem,
            "status": c.status,
            "data": c.data_criacao.strftime("%d/%m/%Y")
        }
        for c in chamados
    ]

@router.put("/{cliente_id}", response_model=ClienteResponse)
async def atualizar_cliente(
    cliente_id: int, 
    cliente_update: ClienteUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Atualiza os dados de um cliente específico."""
    result = await db.execute(select(Cliente).filter(Cliente.id == cliente_id))
    db_cliente = result.scalars().first()
    
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
    update_data = cliente_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_cliente, key, value)
        
    await db.commit()
    await db.refresh(db_cliente)
    return db_cliente

@router.delete("/{cliente_id}")
async def deletar_cliente(
    cliente_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Remove um cliente do sistema."""
    result = await db.execute(select(Cliente).filter(Cliente.id == cliente_id))
    db_cliente = result.scalars().first()
    
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
    await db.delete(db_cliente)
    await db.commit()
    return {"message": "Cliente removido com sucesso"}

@router.get("/telefone/{telefone}", response_model=ClienteResponse)
async def buscar_cliente_por_telefone(
    telefone: str, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Busca um cliente pelo número de telefone."""
    result = await db.execute(select(Cliente).filter(Cliente.telefone == telefone))
    cliente = result.scalars().first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

@router.get("/email/{email}", response_model=ClienteResponse)
async def buscar_cliente_por_email_admin(
    email: str, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Busca um cliente pelo email (Rota autenticada para Admin/CRM)."""
    result = await db.execute(select(Cliente).filter(Cliente.email == email))
    cliente = result.scalars().first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

@router.get("/{cliente_id}/chamados")
async def listar_chamados_cliente(
    cliente_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lista todos os chamados de um cliente específico."""
    from src.models.chamado import Chamado
    result = await db.execute(
        select(Chamado).filter(Chamado.cliente_id == cliente_id).order_by(Chamado.data_criacao.desc())
    )
    return result.scalars().all()

@router.get("/{cliente_id}/plano")
async def obter_plano_cliente(
    cliente_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Retorna o último plano ativo de um cliente específico."""
    from src.models.contrato import Contrato
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(Contrato)
        .options(selectinload(Contrato.plano))
        .filter(Contrato.cliente_id == cliente_id, Contrato.status == 'ativo')
        .order_by(Contrato.data_inicio.desc())
    )
    contrato = result.scalars().first()
    
    if not contrato:
        raise HTTPException(status_code=404, detail="Nenhum plano ativo encontrado")
    return contrato.plano

@router.get("/me/resumo")
async def obter_meu_resumo(
    db: AsyncSession = Depends(get_db),
    current_client: Cliente = Depends(get_current_client)
):
    """Retorna um resumo completo dos dados do cliente autenticado."""
    
    # 1. Get Active Plan
    from src.models.contrato import Contrato
    from sqlalchemy.orm import selectinload
    contrato_result = await db.execute(
        select(Contrato)
        .options(selectinload(Contrato.plano))
        .filter(Contrato.cliente_id == current_client.id, Contrato.status == 'ativo')
        .order_by(Contrato.data_inicio.desc())
    )
    contrato = contrato_result.scalars().first()
    
    # 2. Get Last 5 Tickets
    from src.models.chamado import Chamado
    chamados_result = await db.execute(
        select(Chamado)
        .filter(Chamado.cliente_id == current_client.id)
        .order_by(Chamado.data_criacao.desc())
        .limit(5)
    )
    chamados = chamados_result.scalars().all()

    # 3. Get Pending Invoices
    from src.models.fatura import Fatura
    from src.models.contrato import Contrato
    
    faturas_result = await db.execute(
        select(Fatura)
        .join(Contrato)
        .filter(Contrato.cliente_id == current_client.id, Fatura.status == 'pendente')
        .order_by(Fatura.data_vencimento.asc())
        .limit(3)
    )
    faturas = faturas_result.scalars().all()
    
    return {
        "cliente": current_client,
        "plano_ativo": contrato.plano if contrato else None,
        "ultimos_chamados": chamados,
        "faturas_pendentes": faturas
    }



