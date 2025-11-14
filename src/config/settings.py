"""
Módulo para centralizar as configurações da aplicação.

Utiliza Pydantic-Settings para carregar variáveis de ambiente
e validá-las, garantindo que a aplicação inicie apenas com
configurações corretas.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, Field
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Configurações da aplicação carregadas a partir de variáveis de ambiente.
    """

    # Carrega as variáveis de um arquivo .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # ==================== DATABASE ====================
    DATABASE_URL: PostgresDsn = Field(
        ...,
        description="URL de conexão com o banco de dados PostgreSQL.",
        examples=["postgresql://user:password@host:port/database"],
    )

    # ==================== APLICAÇÃO ====================
    APP_ENV: str = Field("development", description="Ambiente da aplicação.")
    APP_DEBUG: bool = Field(False, description="Modo de depuração.")
    APP_HOST: str = Field("0.0.0.0", description="Host da aplicação.")
    APP_PORT: int = Field(8000, description="Porta da aplicação.")

    # ==================== AZURE (Opcional) ====================
    AZURE_COGNITIVE_KEY: Optional[str] = Field(
        None, description="Chave da API do Azure Cognitive Services."
    )
    AZURE_COGNITIVE_ENDPOINT: Optional[str] = Field(
        None, description="Endpoint do Azure Cognitive Services."
    )

    # ==================== LOGGING ====================
    LOG_LEVEL: str = Field("INFO", description="Nível de log.")


# Instância única das configurações para ser importada em outros módulos
try:
    settings = Settings()
    logger.info("✅ Configurações da aplicação carregadas com sucesso.")
except Exception as e:
    logger.error(f"❌ Erro ao carregar as configurações: {e}")
    raise

