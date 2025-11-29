"""
Script para resetar o banco de dados.

ATENÇÃO: Este script apagará TODOS os dados das tabelas
e as recriará com base nos modelos atuais do SQLAlchemy.

Use com cuidado.
"""

import logging

from src.config.database import Base, engine

# Configura um logger básico para ver o que está acontecendo
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_database():
    """Apaga e recria todas as tabelas."""
    try:
        logger.info("Iniciando o reset do banco de dados...")

        # Importa todos os modelos para que eles sejam registrados no Base.metadata
        # Mesmo que não sejam usados diretamente, a importação é necessária.
        from src.models.user import User  # noqa
        from src.models.cliente import Cliente  # noqa
        from src.models.chamado import Chamado  # noqa
        from src.models.metrica import Metrica # noqa

        logger.warning("APAGANDO todas as tabelas existentes...")
        Base.metadata.drop_all(bind=engine)
        logger.info("Tabelas apagadas com sucesso.")

        logger.info("CRIANDO todas as tabelas a partir dos modelos...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso.")

        logger.info("✅ Reset do banco de dados concluído!")

    except Exception as e:
        logger.error(f"❌ Ocorreu um erro durante o reset do banco de dados: {e}")
        raise


if __name__ == "__main__":
    reset_database()
