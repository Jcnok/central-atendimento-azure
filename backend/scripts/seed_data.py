import asyncio
import logging
import sys
import os
from datetime import date, timedelta

# Add project root to python path
sys.path.append(os.getcwd())

from src.config.database import init_db, close_db, AsyncSessionLocal, engine, Base
from src.models import (
    User, Cliente, Plano, Contrato, Fatura, Pagamento, Chamado, Atendente, HistoricoAtendimento
)
from src.utils.protocolo import gerar_protocolo
from src.utils.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed():
    logger.info("🌱 Iniciando Seeding...")
    
    # Recreate tables (Force Cascade)
    async with engine.begin() as conn:
        # Disable foreign key checks to allow dropping in any order (for Postgres this is different, but CASCADE works)
        # For PostgreSQL, we can drop the schema public and recreate it, or drop tables with CASCADE.
        # Let's try dropping tables explicitly with CASCADE if drop_all fails.
        
        from sqlalchemy import text
        # Get all table names
        # This is a bit hacky but ensures we clean up everything
        tables = ["historico_atendimentos", "pagamentos", "faturas", "chamados", "contratos", "clientes", "planos", "atendentes", "users", "metricas"]
        for table in tables:
            await conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # 1. Create Admin User
        admin = User(
            email="admin@central.com",
            hashed_password=get_password_hash("admin"),
            is_active=True,
            is_superuser=True,
            full_name="Administrador do Sistema"
        )
        session.add(admin)
        
        # 2. Create Atendentes
        atendentes = [
            Atendente(nome="Carlos Técnico", email="carlos@central.com", especialidade="tecnico"),
            Atendente(nome="Ana Financeiro", email="ana@central.com", especialidade="financeiro"),
            Atendente(nome="Roberto Vendas", email="roberto@central.com", especialidade="vendas"),
            Atendente(nome="Sofia Geral", email="sofia@central.com", especialidade="geral"),
        ]
        session.add_all(atendentes)
        
        # 3. Create Plans
        planos = [
            Plano(nome="Internet Fibra 500MB", descricao="Internet ultra rápida para sua casa", velocidade="500MB", preco=120.00, tipo="internet"),
            Plano(nome="Internet Fibra 1GB", descricao="Máxima velocidade para gamers e streamers", velocidade="1GB", preco=200.00, tipo="internet"),
            Plano(nome="Móvel 5G Ilimitado", descricao="Dados ilimitados e ligações para todo Brasil", velocidade="5G", preco=89.90, tipo="movel"),
            Plano(nome="TV 4K Premium", descricao="Mais de 200 canais em 4K", velocidade="N/A", preco=150.00, tipo="tv"),
        ]
        session.add_all(planos)
        await session.flush() # To get IDs
        
        # 4. Create Clients
        clientes = []
        for i in range(1, 6):
            cliente = Cliente(
                nome=f"Cliente {i}",
                email=f"cliente{i}@email.com",
                hashed_password=get_password_hash("123456"), # Default password
                telefone=f"1199999000{i}",
                endereco=f"Rua Exemplo, {100+i}, São Paulo - SP",
                canal_preferido="site"
            )
            clientes.append(cliente)
        session.add_all(clientes)
        await session.flush()
        
        # 5. Create Contracts & Faturas
        for cliente in clientes:
            # Give each client a random plan (or specifically the first one for simplicity)
            plano = planos[0] 
            contrato = Contrato(
                cliente_id=cliente.id,
                plano_id=plano.plano_id,
                data_inicio=date.today() - timedelta(days=365),
                status="ativo",
                tipo_servico=plano.tipo
            )
            session.add(contrato)
            await session.flush()
            
            # Create Invoices (Last 3 months)
            for m in range(3):
                data_emissao = date.today() - timedelta(days=30 * (m+1))
                data_vencimento = data_emissao + timedelta(days=10)
                status = "pago" if m > 0 else "pendente" # Oldest are paid, newest is pending
                
                fatura = Fatura(
                    contrato_id=contrato.contrato_id,
                    data_emissao=data_emissao,
                    data_vencimento=data_vencimento,
                    valor=plano.preco,
                    status=status
                )
                session.add(fatura)
                await session.flush()
                
                if status == "pago":
                    pagamento = Pagamento(
                        fatura_id=fatura.fatura_id,
                        data_pagamento=data_vencimento, # Paid on due date
                        valor_pago=plano.preco,
                        forma_pagamento="pix"
                    )
                    session.add(pagamento)

        # 6. Create Tickets (Chamados)
        chamado_aberto = Chamado(
            protocolo=gerar_protocolo(),
            cliente_id=clientes[0].id,
            canal="site",
            mensagem="Minha internet está lenta.",
            status="aberto",
            prioridade="alta",
            categoria="tecnico"
        )
        session.add(chamado_aberto)
        
        chamado_fechado = Chamado(
            protocolo=gerar_protocolo(),
            cliente_id=clientes[0].id,
            canal="whatsapp",
            mensagem="Quero a segunda via do boleto.",
            status="resolvido",
            prioridade="baixa",
            categoria="financeiro",
            resolucao="Boleto enviado por email.",
            data_fechamento=date.today()
        )
        session.add(chamado_fechado)

        await session.commit()
        logger.info("✅ Seeding concluído com sucesso!")

if __name__ == "__main__":
    asyncio.run(seed())
