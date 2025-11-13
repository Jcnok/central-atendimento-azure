"""
Configuração de conexão com PostgreSQL via SQLAlchemy
SEGURO: Usa variáveis de ambiente, sem credenciais hardcoded
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv
import logging

# Carregar variáveis de ambiente
load_dotenv()

logger = logging.getLogger(__name__)

# ==================== VALIDAÇÃO DE CREDENCIAIS ====================

DATABASE_URL = os.getenv("DATABASE_URL")

# Validar se DATABASE_URL está definida
if not DATABASE_URL:
    raise ValueError(
        "❌ ERRO CRÍTICO: Variável DATABASE_URL não está definida!\n"
        "Por favor, defina a variável de ambiente DATABASE_URL com a string de conexão.\n"
        "Exemplo: postgresql://user:password@host:port/database\n"
        "Verifique o arquivo .env ou as variáveis de ambiente do seu sistema."
    )

# Validar formato mínimo
if not DATABASE_URL.startswith("postgresql://"):
    logger.warning("⚠️  DATABASE_URL não parece ser uma conexão PostgreSQL válida")

# ==================== SQLALCHEMY ENGINE ====================

try:
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,  # Importante para Azure (conexões limitadas em tier free)
        echo=False,  # Mude para True apenas em desenvolvimento para debug
        connect_args={
            "connect_timeout": 10,
            "application_name": "central-atendimento-api"
        }
    )
    logger.info("✅ Engine SQLAlchemy criado com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao criar engine: {str(e)}")
    raise

# ==================== SESSION FACTORY ====================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

Base = declarative_base()

# ==================== DEPENDENCY ====================

def get_db():
    """
    Dependency para injetar sessão no FastAPI
    Garante que a sessão é fechada após cada requisição
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

# ==================== INICIALIZAÇÃO ====================

def init_db():
    """
    Cria todas as tabelas no banco de dados
    Chamada automaticamente no startup da aplicação
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tabelas do banco de dados criadas/validadas com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar banco: {str(e)}")
        raise

def close_db():
    """Fecha todas as conexões (usar no shutdown da app)"""
    engine.dispose()
    logger.info("✅ Conexões do banco fechadas")
