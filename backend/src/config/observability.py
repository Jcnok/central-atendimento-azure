import logging
from fastapi import FastAPI
from src.config.settings import settings

logger = logging.getLogger(__name__)

def setup_observability(app: FastAPI):
    """
    Configures OpenTelemetry and Azure Monitor if available.
    """
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        
        if settings.APPLICATIONINSIGHTS_CONNECTION_STRING:
            configure_azure_monitor(
                connection_string=settings.APPLICATIONINSIGHTS_CONNECTION_STRING,
                logger_name=__name__
            )
            logger.info("✅ Azure Monitor configured successfully")
            
            # Instrument FastAPI
            FastAPIInstrumentor.instrument_app(app)
            logger.info("✅ FastAPI instrumentation enabled")
        else:
            logger.info("ℹ️ Azure Monitor connection string not found. Skipping observability setup.")
            
    except ImportError as e:
        logger.warning(f"⚠️ Observability dependencies not found: {e}. Skipping setup.")
    except Exception as e:
        logger.error(f"❌ Error setting up observability: {e}")
