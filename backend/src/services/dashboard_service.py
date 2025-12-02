from sqlalchemy import func, select, desc, case, extract
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.chamado import Chamado
from src.models.cliente import Cliente
from src.models.contrato import Contrato
from datetime import datetime, timedelta

class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_kpis(self):
        # 1. Total Clientes
        total_clientes = (await self.db.execute(select(func.count(Cliente.id)))).scalar() or 0
        
        # 2. Contratos Ativos e Cancelados (Churn)
        total_contratos = (await self.db.execute(select(func.count(Contrato.contrato_id)))).scalar() or 0
        contratos_ativos = (await self.db.execute(
            select(func.count(Contrato.contrato_id)).filter(Contrato.status == 'ativo')
        )).scalar() or 0
        contratos_cancelados = (await self.db.execute(
            select(func.count(Contrato.contrato_id)).filter(Contrato.status == 'cancelado')
        )).scalar() or 0
        
        churn_rate = 0
        if total_contratos > 0:
            churn_rate = round((contratos_cancelados / total_contratos) * 100, 2)

        # 3. Chamados e IA Stats
        total_chamados = (await self.db.execute(select(func.count(Chamado.id)))).scalar() or 0
        chamados_abertos = (await self.db.execute(
            select(func.count(Chamado.id)).filter(Chamado.status == 'aberto')
        )).scalar() or 0
        
        # Chamados resolvidos pela IA (canal='chat_ia' e status='resolvido' e encaminhado_para_humano=False)
        chamados_ia_resolvidos = (await self.db.execute(
            select(func.count(Chamado.id)).filter(
                Chamado.canal == 'chat_ia',
                Chamado.status == 'resolvido',
                Chamado.encaminhado_para_humano == False
            )
        )).scalar() or 0
        
        ai_resolution_rate = 0
        if total_chamados > 0:
            ai_resolution_rate = round((chamados_ia_resolvidos / total_chamados) * 100, 2)

        # 4. Financeiro (Estimativa)
        # Custo Humano Médio por Chamado: R$ 15,00
        # Custo IA Médio por Chamado: R$ 0,50
        custo_humano_unitario = 15.00
        custo_ia_unitario = 0.50
        
        # Economia Gerada = (Chamados IA * Custo Humano) - (Chamados IA * Custo IA)
        economia_total = chamados_ia_resolvidos * (custo_humano_unitario - custo_ia_unitario)
        
        # Receita Estimada (Mock baseada em contratos ativos * ticket médio R$ 100)
        receita_mensal = contratos_ativos * 100.00
        custo_operacional = (total_chamados - chamados_ia_resolvidos) * custo_humano_unitario + (chamados_ia_resolvidos * custo_ia_unitario)
        
        profit_margin = 0
        if receita_mensal > 0:
            profit_margin = round(((receita_mensal - custo_operacional) / receita_mensal) * 100, 2)

        return {
            "total_clientes": total_clientes,
            "contratos_ativos": contratos_ativos,
            "chamados_abertos": chamados_abertos,
            "churn_rate": f"{churn_rate}%",
            "ai_resolution_rate": f"{ai_resolution_rate}%",
            "total_savings": f"R$ {economia_total:,.2f}",
            "profit_margin": f"{profit_margin}%",
            "nps_medio": 78,  # Mock fixo por enquanto
            "avg_ai_response_time": "1.2s", # Mock
            "first_contact_resolution": "82%" # Mock
        }

    async def get_recent_tickets(self, limit: int = 10):
        query = select(Chamado).order_by(desc(Chamado.data_criacao)).limit(limit)
        result = await self.db.execute(query)
        chamados = result.scalars().all()
        
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

    async def get_tickets_by_channel(self):
        # Agrupa chamados por canal
        query = select(Chamado.canal, func.count(Chamado.id)).group_by(Chamado.canal)
        result = await self.db.execute(query)
        data = [{"name": row[0], "value": row[1]} for row in result.all()]
        return data

    async def get_tickets_evolution(self):
        # Agrupa chamados por data (últimos 7 dias)
        # Nota: SQLite e Postgres têm funções de data diferentes. 
        # Para simplificar e ser compatível, vamos pegar os dados brutos e processar no Python ou usar func.date se for Postgres.
        # Aqui faremos uma query simples dos últimos 7 dias e agruparemos no Python para garantir compatibilidade.
        
        seven_days_ago = datetime.now() - timedelta(days=7)
        query = select(Chamado.data_criacao).filter(Chamado.data_criacao >= seven_days_ago)
        result = await self.db.execute(query)
        dates = result.scalars().all()
        
        # Processamento no Python
        from collections import Counter
        date_counts = Counter([d.strftime('%Y-%m-%d') for d in dates])
        
        # Ordenar e formatar
        sorted_dates = sorted(date_counts.items())
        return [{"date": date, "count": count} for date, count in sorted_dates]
