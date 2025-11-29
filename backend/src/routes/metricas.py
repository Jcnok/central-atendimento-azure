from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import get_db
from src.models.chamado import Chamado
from src.models.cliente import Cliente
from src.utils.security import get_current_user

router = APIRouter(prefix="/metricas", tags=["Métricas"])


@router.get("/", response_model=dict, dependencies=[Depends(get_current_user)])
async def obter_metricas(db: AsyncSession = Depends(get_db)):
    """Retorna métricas gerais de atendimento"""

    total_chamados_result = await db.execute(select(func.count(Chamado.id)))
    total_chamados = total_chamados_result.scalar() or 0
    
    chamados_automaticos_result = await db.execute(
        select(func.count(Chamado.id)).filter(Chamado.encaminhado_para_humano == False)
    )
    chamados_automaticos = chamados_automaticos_result.scalar() or 0
    
    chamados_encaminhados_result = await db.execute(
        select(func.count(Chamado.id)).filter(Chamado.encaminhado_para_humano == True)
    )
    chamados_encaminhados = chamados_encaminhados_result.scalar() or 0

    total_clientes_result = await db.execute(select(func.count(Cliente.id)))
    total_clientes = total_clientes_result.scalar() or 0

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


@router.get(
    "/por-canal", response_model=dict, dependencies=[Depends(get_current_user)]
)
async def metricas_por_canal(db: AsyncSession = Depends(get_db)):
    """Retorna métricas detalhadas por canal"""
    canais = ["site", "whatsapp", "email"]
    resultado = {}

    for canal in canais:
        total_result = await db.execute(
            select(func.count(Chamado.id)).filter(Chamado.canal == canal)
        )
        total = total_result.scalar() or 0
        
        automaticos_result = await db.execute(
            select(func.count(Chamado.id))
            .filter(Chamado.canal == canal, Chamado.encaminhado_para_humano == False)
        )
        automaticos = automaticos_result.scalar() or 0

        resultado[canal] = {
            "total": total,
            "resolvidos_automaticamente": automaticos,
            "taxa_resolucao": f"{(automaticos/total*100):.1f}%" if total > 0 else "0%",
        }

    return resultado


@router.get(
    "/por-status", response_model=dict, dependencies=[Depends(get_current_user)]
)
async def metricas_por_status(db: AsyncSession = Depends(get_db)):
    """Retorna distribuição de chamados por status"""
    statuses = ["aberto", "resolvido", "encaminhado"]
    resultado = {}

    for status in statuses:
        count_result = await db.execute(
            select(func.count(Chamado.id)).filter(Chamado.status == status)
        )
        count = count_result.scalar() or 0
        resultado[status] = count

    return resultado
