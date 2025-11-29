from .chamados import router as chamados_router
from .clientes import router as clientes_router
from .metricas import router as metricas_router

__all__ = ["clientes_router", "chamados_router", "metricas_router"]
