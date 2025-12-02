from typing import Dict, Optional
from datetime import date, timedelta
from sqlalchemy import select
from src.config.database import AsyncSessionLocal
from src.models.cliente import Cliente
from src.models.contrato import Contrato
from src.models.plano import Plano
from src.models.fatura import Fatura
from src.utils.security import get_password_hash

class SubscriptionService:
    @staticmethod
    async def create_subscription(
        nome: str, 
        email: str, 
        plano_nome: str, 
        cpf: str,
        endereco: str,
        telefone: str = "11999999999", 
        canal: str = "chat_ia"
    ) -> Dict[str, any]:
        """
        Executa o fluxo de venda de forma atômica:
        1. Verifica/Cria Cliente
        2. Busca Plano
        3. Cria Contrato
        4. Gera Fatura
        """
        async with AsyncSessionLocal() as session:
            try:
                # 1. Busca Plano (Fuzzy Match)
                result_plano = await session.execute(select(Plano).filter(Plano.nome.ilike(f"%{plano_nome}%")))
                plano = result_plano.scalars().first()
                
                if not plano:
                    return {"error": f"Plano '{plano_nome}' não encontrado. Planos disponíveis: Fibra 500MB, Fibra 1GB, Móvel 5G."}

                # 2. Verifica Cliente Existente
                result_cliente = await session.execute(select(Cliente).filter(Cliente.email == email))
                existing_client = result_cliente.scalars().first()
                
                if existing_client:
                    return {"error": "Email já cadastrado. Por favor, faça login para contratar novas linhas."}

                # 3. Cria Cliente
                novo_cliente = Cliente(
                    nome=nome,
                    email=email,
                    hashed_password=get_password_hash("123mudar"),
                    telefone=telefone,
                    endereco=endereco,
                    cpf=cpf,
                    canal_preferido=canal
                )
                session.add(novo_cliente)
                await session.flush() # Garante o ID

                # 4. Cria Contrato
                contrato = Contrato(
                    cliente_id=novo_cliente.id,
                    plano_id=plano.plano_id,
                    data_inicio=date.today(),
                    status="ativo",
                    tipo_servico=plano.tipo
                )
                session.add(contrato)
                await session.flush()

                # 5. Gera Fatura (Boleto)
                fatura = Fatura(
                    contrato_id=contrato.contrato_id,
                    data_emissao=date.today(),
                    data_vencimento=date.today() + timedelta(days=5),
                    valor=plano.preco,
                    status="pendente"
                )
                session.add(fatura)
                
                await session.commit()
                
                return {
                    "success": True,
                    "cliente_nome": novo_cliente.nome,
                    "plano_nome": plano.nome,
                    "plano_velocidade": plano.velocidade,
                    "valor": float(plano.preco),
                    "fatura_id": fatura.fatura_id,
                    "senha_provisoria": "123mudar"
                }

            except Exception as e:
                await session.rollback()
                return {"error": f"Erro interno ao processar contratação: {str(e)}"}
