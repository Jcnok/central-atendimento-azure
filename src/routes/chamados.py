from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

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
def criar_chamado(
    chamado: ChamadoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Cria um novo chamado (ticket de atendimento)
    Automaticamente classifica com IA e decide se resolve ou encaminha
    """
    # Verifica se cliente existe
    cliente = db.query(Cliente).filter(Cliente.id == chamado.cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado"
        )

    # Classifica a mensagem com IA
    classificacao = IAClassifier.classificar(chamado.mensagem, chamado.canal)

    # Cria o chamado no banco
    novo_chamado = Chamado(
        cliente_id=chamado.cliente_id,
        user_id=current_user.id,
        canal=chamado.canal,
        mensagem=chamado.mensagem,
        status="resolvido" if classificacao["resolvido"] else "aberto",
        resposta_automatica=classificacao["resposta"],
        encaminhado_para_humano=not classificacao["resolvido"],
    )

    db.add(novo_chamado)
    db.commit()
    db.refresh(novo_chamado)

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
    "/{chamado_id}",
    response_model=ChamadoResponse,
    dependencies=[Depends(get_current_user)],
)
def obter_chamado(chamado_id: int, db: Session = Depends(get_db)):
    """Obtém informações de um chamado específico"""
    chamado = db.query(Chamado).filter(Chamado.id == chamado_id).first()
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
def listar_chamados(
    status_filtro: str = None,
    canal: str = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    Lista chamados com filtros opcionais
    Filtros: status (aberto, resolvido, encaminhado), canal (site, whatsapp, email)
    """
    query = db.query(Chamado)

    if status_filtro:
        query = query.filter(Chamado.status == status_filtro)

    if canal:
        query = query.filter(Chamado.canal == canal)

    chamados = (
        query.order_by(desc(Chamado.data_criacao)).offset(skip).limit(limit).all()
    )
    return chamados


@router.put(
    "/{chamado_id}",
    response_model=ChamadoResponse,
    dependencies=[Depends(get_current_user)],
)
def atualizar_chamado_status(
    chamado_id: int, novo_status: str, db: Session = Depends(get_db)
):
    """Atualiza o status de um chamado"""
    chamado = db.query(Chamado).filter(Chamado.id == chamado_id).first()
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
    db.commit()
    db.refresh(chamado)

    return chamado


@router.get(
    "/cliente/{cliente_id}",
    response_model=list[ChamadoResponse],
    dependencies=[Depends(get_current_user)],
)
def listar_chamados_por_cliente(
    cliente_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Lista todos os chamados de um cliente específico"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado"
        )

    chamados = (
        db.query(Chamado)
        .filter(Chamado.cliente_id == cliente_id)
        .order_by(desc(Chamado.data_criacao))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return chamados
