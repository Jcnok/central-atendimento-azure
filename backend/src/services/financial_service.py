from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.config.database import AsyncSessionLocal
from src.models.fatura import Fatura
from src.models.contrato import Contrato
from src.models.cliente import Cliente

class FinancialService:
    @staticmethod
    async def gerar_boleto_simulado(email: str, cpf: Optional[str] = None) -> Optional[Dict[str, any]]:
        """
        Gera uma 2ª via de boleto simulada (busca a última fatura pendente).
        """
        async with AsyncSessionLocal() as session:
            # Find client by email
            result = await session.execute(select(Cliente).filter(Cliente.email == email))
            cliente = result.scalars().first()
            
            if not cliente:
                return None

            # Find latest pending invoice
            result_fatura = await session.execute(
                select(Fatura)
                .join(Contrato)
                .filter(Contrato.cliente_id == cliente.id, Fatura.status == 'pendente')
                .order_by(Fatura.data_vencimento.asc())
            )
            fatura = result_fatura.scalars().first()
            
            if not fatura:
                return None

            return {
                "mensagem": "2ª Via gerada com sucesso",
                "codigo_barras": f"34191.79001 01043.510047 91020.150008 8 {fatura.fatura_id}0000015000",
                "link_pdf": f"https://central.com/faturas/{fatura.fatura_id}.pdf",
                "valor": float(fatura.valor),
                "vencimento": fatura.data_vencimento.strftime("%d/%m/%Y"),
            }

    @staticmethod
    async def check_payment_status(boleto_id: str) -> str:
        """
        Verifica o status de um pagamento pelo ID da fatura.
        """
        try:
            fatura_id = int(boleto_id)
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(Fatura).filter(Fatura.fatura_id == fatura_id))
                fatura = result.scalars().first()
                return fatura.status if fatura else "não encontrado"
        except ValueError:
            return "ID inválido"

    @staticmethod
    async def get_invoices(cliente_id: int) -> List[Dict[str, any]]:
        """
        Retorna lista de faturas reais do banco.
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Fatura)
                .join(Contrato)
                .filter(Contrato.cliente_id == cliente_id)
                .order_by(Fatura.data_vencimento.desc())
                .limit(5)
            )
            faturas = result.scalars().all()
            
            return [
                {
                    "id": str(f.fatura_id),
                    "valor": float(f.valor),
                    "status": f.status,
                    "vencimento": f.data_vencimento.strftime("%Y-%m-%d")
                }
                for f in faturas
            ]
