from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.config.database import get_db
from src.models.cliente import Cliente
from src.schemas.cliente import ClienteCreate, ClienteResponse
from src.utils.security import get_current_user

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



