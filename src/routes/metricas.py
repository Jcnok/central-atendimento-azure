from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.models.chamado import Chamado
from src.models.cliente import Cliente

router = APIRouter(prefix="/metricas", tags=["Métricas"])


@router.get("/", response_model=dict)
def obter_metricas(db: Session = Depends(get_db)):
    """Retorna métricas gerais de atendimento"""

    total_chamados = db.query(func.count(Chamado.id)).scalar() or 0
    chamados_automaticos = (
        db.query(func.count(Chamado.id))
        .filter(Chamado.encaminhado_para_humano == False)
        .scalar()
        or 0
    )
    chamados_encaminhados = (
        db.query(func.count(Chamado.id))
        .filter(Chamado.encaminhado_para_humano == True)
        .scalar()
        or 0
    )

    total_clientes = db.query(func.count(Cliente.id)).scalar() or 0

    taxa_resolucao = (
        (chamados_automaticos / total_chamados * 100) if total_chamados > 0 else 0
    )

    return {
        "total_chamados": total_chamados,
        "total_clientes": total_clientes,
        "chamados_resolvidos_automaticamente": chamados_automaticos,
        "chamados_encaminhados_para_humano": chamados_encaminhados,
        "taxa_resolucao_automatica": f"{taxa_resolucao:.1f}%",
        "tempo_medio_resposta_segundos": "< 1s (mock)",
    }


@router.get("/por-canal", response_model=dict)
def metricas_por_canal(db: Session = Depends(get_db)):
    """Retorna métricas detalhadas por canal"""
    canais = ["site", "whatsapp", "email"]
    resultado = {}

    for canal in canais:
        total = (
            db.query(func.count(Chamado.id)).filter(Chamado.canal == canal).scalar()
            or 0
        )
        automaticos = (
            db.query(func.count(Chamado.id))
            .filter(Chamado.canal == canal, Chamado.encaminhado_para_humano == False)
            .scalar()
            or 0
        )

        resultado[canal] = {
            "total": total,
            "resolvidos_automaticamente": automaticos,
            "taxa_resolucao": f"{(automaticos/total*100):.1f}%" if total > 0 else "0%",
        }

    return resultado


@router.get("/por-status", response_model=dict)
def metricas_por_status(db: Session = Depends(get_db)):
    """Retorna distribuição de chamados por status"""
    statuses = ["aberto", "resolvido", "encaminhado"]
    resultado = {}

    for status in statuses:
        count = (
            db.query(func.count(Chamado.id)).filter(Chamado.status == status).scalar()
            or 0
        )
        resultado[status] = count

    return resultado
