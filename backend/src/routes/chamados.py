from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import get_db
from src.models.chamado import Chamado
from src.models.cliente import Cliente
from src.schemas.chamado import (
    ChamadoCreate,
    ChamadoCreateResponse,
    ChamadoResponse,
)
from src.services.ia_classifier import IAClassifier
from src.utils.security import get_current_user

router = APIRouter(prefix="/chamados", tags=["Chamados"])


@router.post(
    "/",
    response_model=ChamadoCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def criar_chamado(
    chamado: ChamadoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Cria um novo chamado (ticket de atendimento)
    Automaticamente classifica com IA e decide se resolve ou encaminha
    """
    # Verifica se cliente existe
    result = await db.execute(select(Cliente).filter(Cliente.id == chamado.cliente_id))
    cliente = result.scalars().first()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado"
        )

    # Classifica a mensagem com IA
    # Nota: Se IAClassifier.classificar for bloqueante (requests sync), deveria rodar em threadpool ou ser async
    # Assumindo que é sync por enquanto, mas rápido. Se for lento, precisa de run_in_executor.
    classificacao = IAClassifier.classificar(chamado.mensagem, chamado.canal)

    # Cria o chamado no banco
    from src.utils.protocolo import gerar_protocolo
    
    novo_chamado = Chamado(
        cliente_id=chamado.cliente_id,
        user_id=current_user.id,
        protocolo=gerar_protocolo(),
        canal=chamado.canal,
        mensagem=chamado.mensagem,
        status="resolvido" if classificacao["resolvido"] else "aberto",
        resposta_automatica=classificacao["resposta"],
        encaminhado_para_humano=not classificacao["resolvido"],
        prioridade=classificacao["prioridade"],
        categoria=classificacao["intencao"],
    )

    db.add(novo_chamado)
    await db.commit()
    await db.refresh(novo_chamado)

    return ChamadoCreateResponse(
        chamado_id=novo_chamado.id,
        cliente_id=novo_chamado.cliente_id,
        canal=novo_chamado.canal,
        resposta=classificacao["resposta"],
        resolvido_automaticamente=classificacao["resolvido"],
        prioridade=classificacao["prioridade"],
        encaminhado_para_humano=not classificacao["resolvido"],
        data_criacao=novo_chamado.data_criacao,
    )



@router.post(
    "/public",
    response_model=ChamadoCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def criar_chamado_publico(
    chamado: ChamadoCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Cria um novo chamado publicamente (Autoatendimento)
    Não requer autenticação de usuário.
    """
    # Verifica se cliente existe
    result = await db.execute(select(Cliente).filter(Cliente.id == chamado.cliente_id))
    cliente = result.scalars().first()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado"
        )

    # Classifica a mensagem com IA
    classificacao = IAClassifier.classificar(chamado.mensagem, chamado.canal)

    # Cria o chamado no banco (sem user_id)
    from src.utils.protocolo import gerar_protocolo

    novo_chamado = Chamado(
        cliente_id=chamado.cliente_id,
        user_id=None,
        protocolo=gerar_protocolo(),
        canal=chamado.canal,
        mensagem=chamado.mensagem,
        status="resolvido" if classificacao["resolvido"] else "encaminhado",
        resposta_automatica=classificacao["resposta"],
        encaminhado_para_humano=not classificacao["resolvido"],
        prioridade=classificacao["prioridade"],
        categoria=classificacao["intencao"],
    )

    db.add(novo_chamado)
    await db.commit()
    await db.refresh(novo_chamado)

    return ChamadoCreateResponse(
        chamado_id=novo_chamado.id,
        cliente_id=novo_chamado.cliente_id,
        canal=novo_chamado.canal,
        resposta=classificacao["resposta"],
        resolvido_automaticamente=classificacao["resolvido"],
        prioridade=classificacao["prioridade"],
        encaminhado_para_humano=not classificacao["resolvido"],
        data_criacao=novo_chamado.data_criacao,
    )


@router.get(
    "/public/{chamado_id}",
    response_model=ChamadoResponse,
)
async def obter_chamado_publico(
    chamado_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtém detalhes de um chamado publicamente (Autoatendimento/Chat Widget)
    Não requer autenticação de usuário.
    """
    result = await db.execute(select(Chamado).filter(Chamado.id == chamado_id))
    chamado = result.scalars().first()
    
    if not chamado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chamado não encontrado"
        )
    return chamado


@router.get(
    "/{chamado_id}",
    response_model=ChamadoResponse,
    dependencies=[Depends(get_current_user)],
)
async def obter_chamado(chamado_id: int, db: AsyncSession = Depends(get_db)):
    """Obtém informações de um chamado específico"""
    result = await db.execute(select(Chamado).filter(Chamado.id == chamado_id))
    chamado = result.scalars().first()
    
    if not chamado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chamado não encontrado"
        )
    return chamado


@router.get(
    "/",
    response_model=list[ChamadoResponse],
    dependencies=[Depends(get_current_user)],
)
async def listar_chamados(
    status_filtro: str = None,
    canal: str = None,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """
    Lista chamados com filtros opcionais
    Filtros: status (aberto, resolvido, encaminhado), canal (site, whatsapp, email)
    """
    query = select(Chamado)

    if status_filtro:
        query = query.filter(Chamado.status == status_filtro)

    if canal:
        query = query.filter(Chamado.canal == canal)

    query = query.order_by(desc(Chamado.data_criacao)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    chamados = result.scalars().all()
    
    return chamados


@router.put(
    "/{chamado_id}",
    response_model=ChamadoResponse,
    dependencies=[Depends(get_current_user)],
)
async def atualizar_chamado_status(
    chamado_id: int, novo_status: str, db: AsyncSession = Depends(get_db)
):
    """Atualiza o status de um chamado"""
    result = await db.execute(select(Chamado).filter(Chamado.id == chamado_id))
    chamado = result.scalars().first()
    
    if not chamado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chamado não encontrado"
        )

    status_validos = ["aberto", "resolvido", "encaminhado"]
    if novo_status not in status_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status inválido. Deve ser um de: {status_validos}",
        )

    chamado.status = novo_status
    chamado.data_atualizacao = datetime.now()
    await db.commit()
    await db.refresh(chamado)

    return chamado


@router.get(
    "/cliente/{cliente_id}",
    response_model=list[ChamadoResponse],
    dependencies=[Depends(get_current_user)],
)
async def listar_chamados_por_cliente(
    cliente_id: int, skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    """Lista todos os chamados de um cliente específico"""
    result = await db.execute(select(Cliente).filter(Cliente.id == cliente_id))
    cliente = result.scalars().first()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado"
        )

    query = (
        select(Chamado)
        .filter(Chamado.cliente_id == cliente_id)
        .order_by(desc(Chamado.data_criacao))
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    chamados = result.scalars().all()

    return chamados
