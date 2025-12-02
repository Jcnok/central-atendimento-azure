import asyncio
import logging
import sys
import os
import random
from datetime import date, timedelta, datetime

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

# Listas de nomes para gerar dados realistas
NOMES = ["João", "Maria", "Pedro", "Ana", "Lucas", "Julia", "Marcos", "Fernanda", "Gabriel", "Larissa", "Rafael", "Camila", "Bruno", "Amanda", "Thiago", "Beatriz", "Felipe", "Mariana", "Rodrigo", "Patricia"]
SOBRENOMES = ["Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Almeida", "Pereira", "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho", "Alves", "Monteiro", "Mendes", "Barros", "Freitas", "Barbosa"]

def gerar_nome_completo():
    return f"{random.choice(NOMES)} {random.choice(SOBRENOMES)}"

async def seed():
    logger.info("🌱 Iniciando Seeding Massivo (100+ Clientes)...")
    
    # Recreate tables (Force Cascade)
    async with engine.begin() as conn:
        from sqlalchemy import text
        tables = ["historico_atendimentos", "pagamentos", "faturas", "chamados", "contratos", "clientes", "planos", "atendentes", "users", "metricas"]
        for table in tables:
            await conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            
        # Garante que a extensão vector existe (apenas Postgres)
        if engine.dialect.name == "postgresql":
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # 1. Create Admin User
        admin = User(
            username="admin",
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
            Plano(nome="Internet Fibra 500MB", descricao="Internet ultra rápida", velocidade="500MB", preco=120.00, tipo="internet"),
            Plano(nome="Internet Fibra 1GB", descricao="Máxima velocidade", velocidade="1GB", preco=200.00, tipo="internet"),
            Plano(nome="Móvel 5G Ilimitado", descricao="Dados ilimitados", velocidade="5G", preco=89.90, tipo="movel"),
            Plano(nome="TV 4K Premium", descricao="200 canais em 4K", velocidade="N/A", preco=150.00, tipo="tv"),
        ]
        session.add_all(planos)
        await session.flush()
        
        # 4. Create 100 Clients
        clientes = []
        for i in range(1, 101):
            nome = gerar_nome_completo()
            cliente = Cliente(
                nome=nome,
                email=f"{nome.lower().replace(' ', '.')}{i}@email.com",
                hashed_password=get_password_hash("123456"),
                telefone=f"1199999{str(i).zfill(4)}",
                endereco=f"Rua Exemplo, {i}, São Paulo - SP",
                canal_preferido=random.choice(["whatsapp", "site", "email"])
            )
            clientes.append(cliente)
        session.add_all(clientes)
        await session.flush()
        
        # 5. Create Contracts & Faturas & Chamados
        for cliente in clientes:
            # Random Plan
            plano = random.choice(planos)
            
            # Churn Simulation (approx 5% cancelled)
            status_contrato = "cancelado" if random.random() < 0.05 else "ativo"
            
            contrato = Contrato(
                cliente_id=cliente.id,
                plano_id=plano.plano_id,
                data_inicio=date.today() - timedelta(days=random.randint(30, 700)),
                status=status_contrato,
                tipo_servico=plano.tipo
            )
            session.add(contrato)
            await session.flush()
            
            # Create Tickets (Chamados)
            # 70% of clients have at least one ticket
            if random.random() < 0.7:
                num_tickets = random.randint(1, 3)
                for _ in range(num_tickets):
                    # AI Resolution Simulation
                    # 60% resolved by AI, 40% escalated
                    is_ai_resolved = random.random() < 0.6
                    
                    status_chamado = "resolvido" if is_ai_resolved else random.choice(["aberto", "em_andamento"])
                    canal = "chat_ia" if random.random() < 0.8 else "whatsapp"
                    
                    chamado = Chamado(
                        protocolo=gerar_protocolo(),
                        cliente_id=cliente.id,
                        canal=canal,
                        mensagem="Problema simulado para KPI.",
                        status=status_chamado,
                        prioridade=random.choice(["baixa", "media", "alta"]),
                        categoria=random.choice(["tecnico", "financeiro", "vendas"]),
                        encaminhado_para_humano=not is_ai_resolved,
                        data_criacao=datetime.now() - timedelta(days=random.randint(0, 30)),
                        data_fechamento=datetime.now() if status_chamado == "resolvido" else None
                    )
                    session.add(chamado)

        await session.commit()
        logger.info("✅ Seeding Massivo concluído com sucesso!")

if __name__ == "__main__":
    asyncio.run(seed())
