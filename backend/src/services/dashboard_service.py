from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.chamado import Chamado
from src.models.cliente import Cliente
from src.models.contrato import Contrato

class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_kpis(self):
        # Total Clients
        total_clientes = (await self.db.execute(select(func.count(Cliente.id)))).scalar() or 0
        
        # Active Contracts
        contratos_ativos = (await self.db.execute(
            select(func.count(Contrato.contrato_id)).filter(Contrato.status == 'ativo')
        )).scalar() or 0

        # Open Tickets
        chamados_abertos = (await self.db.execute(
            select(func.count(Chamado.id)).filter(Chamado.status == 'aberto')
        )).scalar() or 0

        # Mocked KPIs for now (would require more complex queries/tables)
        nps_medio = 75  # Mock
        churn_rate = "2.5%" # Mock

        return {
            "total_clientes": total_clientes,
            "contratos_ativos": contratos_ativos,
            "chamados_abertos": chamados_abertos,
            "nps_medio": nps_medio,
            "churn_rate": churn_rate
        }

    async def get_recent_tickets(self, limit: int = 10):
        query = select(Chamado).order_by(desc(Chamado.data_criacao)).limit(limit)
        result = await self.db.execute(query)
        chamados = result.scalars().all()
        
        # Serialize
        return [
            {
                "id": c.id,
                "protocolo": c.protocolo,
                "status": c.status,
                "prioridade": c.prioridade,
                "categoria": c.categoria,
                "data": c.data_criacao.isoformat() if c.data_criacao else None,
                "canal": c.canal
            }
            for c in chamados
        ]
