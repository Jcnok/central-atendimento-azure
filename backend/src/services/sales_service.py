from typing import Dict, List, Optional
from datetime import date, timedelta
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import AsyncSessionLocal
from src.models.cliente import Cliente
from src.models.contrato import Contrato
from src.models.plano import Plano
from src.models.fatura import Fatura
from src.models.chamado import Chamado
from src.utils.protocolo import gerar_protocolo

class SalesService:
    
    @staticmethod
    async def get_customer_profile(cliente_id: int) -> Dict[str, any]:
        """
        Retorna perfil do cliente com dados reais do banco.
        """
        async with AsyncSessionLocal() as session:
            # Get Client and Active Contract
            result = await session.execute(
                select(Contrato).filter(Contrato.cliente_id == cliente_id, Contrato.status == 'ativo')
            )
            contrato = result.scalars().first()
            
            if not contrato:
                return {"error": "Cliente sem contrato ativo."}
                
            # Get Plan details
            result_plano = await session.execute(select(Plano).filter(Plano.plano_id == contrato.plano_id))
            plano = result_plano.scalars().first()
            
            return {
                "cliente_id": cliente_id,
                "current_plan": {
                    "name": plano.nome,
                    "price": float(plano.preco),
                    "speed": plano.velocidade
                },
                "contract_start": contrato.data_inicio.isoformat()
            }

    @staticmethod
    async def get_plan_recommendations(cliente_id: int) -> List[Dict[str, any]]:
        """
        Recomenda planos (Mock logic but async interface).
        """
        # In a real scenario, we would analyze usage data from DB
        return [
            {
                "plan": "Internet Fibra 1GB",
                "reason": "Baseado no seu perfil, o plano de 1GB oferece melhor performance."
            }
        ]

    @staticmethod
    async def calculate_upgrade_cost(current_plan_name: str, new_plan_name: str) -> str:
        """
        Calcula diferença de preço consultando o banco.
        """
        async with AsyncSessionLocal() as session:
            # Helper to find plan by name (fuzzy match or exact)
            async def get_plan_price(name):
                result = await session.execute(select(Plano).filter(Plano.nome.ilike(f"%{name}%")))
                p = result.scalars().first()
                return float(p.preco) if p else 0.0

            current_price = await get_plan_price(current_plan_name)
            new_price = await get_plan_price(new_plan_name)
            
            if new_price == 0:
                return "Plano de destino não encontrado."
                
            diff = new_price - current_price
            
            if diff > 0:
                return f"O upgrade custará R$ {diff:.2f} a mais por mês."
            elif diff < 0:
                return f"Você economizará R$ {abs(diff):.2f} por mês."
            else:
                return "Os planos têm o mesmo preço."

    @staticmethod
    async def upgrade_plan(cliente_id: int, new_plan_name: str) -> str:
        """
        Realiza o upgrade do plano:
        1. Identifica o novo plano.
        2. Atualiza o contrato.
        3. Gera nova fatura pro-rata (simulado como nova fatura cheia para simplificar).
        4. Cria chamado de registro.
        """
        async with AsyncSessionLocal() as session:
            try:
                # 1. Find New Plan
                result_plano = await session.execute(select(Plano).filter(Plano.nome.ilike(f"%{new_plan_name}%")))
                novo_plano = result_plano.scalars().first()
                
                if not novo_plano:
                    return f"Erro: Plano '{new_plan_name}' não encontrado."

                # 2. Update Contract
                result_contrato = await session.execute(
                    select(Contrato).filter(Contrato.cliente_id == cliente_id, Contrato.status == 'ativo')
                )
                contrato = result_contrato.scalars().first()
                
                if not contrato:
                    return "Erro: Cliente sem contrato ativo para upgrade."
                
                contrato.plano_id = novo_plano.plano_id
                session.add(contrato)
                
                # 3. Create New Invoice (Next Month)
                nova_fatura = Fatura(
                    contrato_id=contrato.contrato_id,
                    data_emissao=date.today(),
                    data_vencimento=date.today() + timedelta(days=30),
                    valor=novo_plano.preco,
                    status="pendente"
                )
                session.add(nova_fatura)
                
                # 4. Create Support Ticket (Protocol)
                protocolo = gerar_protocolo()
                chamado = Chamado(
                    protocolo=protocolo,
                    cliente_id=cliente_id,
                    canal="chat_ia",
                    mensagem=f"Upgrade de plano para {novo_plano.nome} realizado via IA.",
                    status="resolvido",
                    prioridade="media",
                    categoria="vendas",
                    resolucao="Alteração de plano efetuada com sucesso.",
                    data_fechamento=date.today()
                )
                session.add(chamado)
                
                await session.commit()
                
                return f"Sucesso! Seu plano foi atualizado para {novo_plano.nome}. Protocolo: {protocolo}. Uma nova fatura foi gerada para o próximo vencimento."
                
            except Exception as e:
                await session.rollback()
                return f"Erro ao processar upgrade: {str(e)}"
