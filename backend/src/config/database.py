"""
Configuração de conexão com PostgreSQL via SQLAlchemy (AsyncIO).

Este módulo utiliza as configurações centralizadas do `src.config.settings`
para criar a engine e a sessão do banco de dados de forma assíncrona.
"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from src.config.settings import settings

logger = logging.getLogger(__name__)

# ===================== ENGINE SQLALCHEMY (ASYNC) =====================

try:
    # Garante que a URL use o driver asyncpg
    database_url = str(settings.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://")
    
    engine = create_async_engine(
        database_url,
        poolclass=NullPool,  # Para conexão limitada (ex: Azure free tier)
        echo=False,
        connect_args={
            "server_settings": {
                "application_name": "central-atendimento-api"
            }
        },
    )
    logger.info("✅ Engine SQLAlchemy Async criada com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao criar engine: {str(e)}")
    raise

# ===================== SESSION FACTORY (ASYNC) =====================

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# ===================== DEPENDENCY FASTAPI =====================


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependência para injeção de sessão assíncrona nas rotas FastAPI
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Erro na sessão do banco: {str(e)}")
            await session.rollback()
            raise
        # O context manager do AsyncSession fecha a sessão automaticamente


# ===================== INICIALIZAÇÃO E FINALIZAÇÃO =====================


# ===================== BASE DECLARATIVA =====================

from sqlalchemy.orm import declarative_base

Base = declarative_base()

# ===================== INICIALIZAÇÃO E FINALIZAÇÃO =====================


# Importar modelos para garantir que sejam registrados no Base
from src.models.user import User  # noqa
from src.models.cliente import Cliente  # noqa
from src.models.chamado import Chamado  # noqa
from src.models.knowledge_base import KnowledgeBaseItem  # noqa


async def init_db():
    """
    Cria todas as tabelas definidas em Base no banco de dados atual.
    Usar no startup da aplicação.
    """
    try:
        async with engine.begin() as conn:
            # Garante que a extensão vector existe
            from sqlalchemy import text
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Tabelas criadas/validadas com sucesso (Async)")
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {str(e)}")
        raise


async def close_db():
    """
    Fecha todas as conexões com o banco.
    """
    await engine.dispose()
    logger.info("✅ Conexões fechadas")
