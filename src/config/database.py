"""
Configuração de conexão com PostgreSQL via SQLAlchemy.

Este módulo utiliza as configurações centralizadas do `src.config.settings`
para criar a engine e a sessão do banco de dados.
"""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from src.config.settings import settings

logger = logging.getLogger(__name__)

# ===================== ENGINE SQLALCHEMY =====================

try:
    # A URL do banco de dados é convertida para string para o create_engine
    engine = create_engine(
        str(settings.DATABASE_URL),
        poolclass=NullPool,  # Para conexão limitada (ex: Azure free tier)
        echo=False,  # Mude para True só se quiser verbose dos comandos SQL
        connect_args={
            "connect_timeout": 10,
            "application_name": "central-atendimento-api",
        },
    )
    logger.info("✅ Engine SQLAlchemy criada com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao criar engine: {str(e)}")
    raise

# ===================== SESSION FACTORY =====================

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)

Base = declarative_base()

# ===================== DEPENDENCY FASTAPI =====================


def get_db():
    """
    Dependência para injeção de sessão nas rotas FastAPI
    Garante fechamento seguro e rollback em caso de erro
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Erro na sessão do banco: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


# ===================== INICIALIZAÇÃO E FINALIZAÇÃO =====================


from src.models.user import User  # noqa
from src.models.cliente import Cliente  # noqa
from src.models.chamado import Chamado  # noqa


def init_db():
    """
    Cria todas as tabelas definidas em Base no banco de dados atual.
    Usar no startup da aplicação (ex: eventos FastAPI).
    SEGURANÇA: Funciona no banco selecionado pelo ambiente (.env)
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tabelas criadas/validadas com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {str(e)}")
        raise


def close_db():
    """
    Fecha todas as conexões com o banco.
    Usar no shutdown da aplicação.
    """
    engine.dispose()
    logger.info("✅ Conexões fechadas")
