"""
Central de Atendimento Automática com IA
API FastAPI para orquestração de tickets, clientes e automação de atendimento
Otimizado para Azure App Service com PostgreSQL
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config.database import close_db, init_db
from src.routes.auth import router as auth_router
from src.routes.chamados import router as chamados_router
from src.routes.clientes import router as clientes_router
from src.routes.metricas import router as metricas_router

# ==================== CONFIGURAÇÃO DE LOGGING ====================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== GERENCIADOR DE CICLO DE VIDA (LIFESPAN) ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de ciclo de vida da aplicação.
    Executa tarefas de inicialização (startup) e finalização (shutdown).
    """
    logger.info("🚀 Iniciando aplicação...")
    init_db()  # Inicializa o banco de dados
    logger.info("✅ Banco de dados inicializado!")
    yield  # A aplicação roda aqui
    logger.info("🛑 Encerrando aplicação...")
    close_db()  # Fecha as conexões com o banco de dados


from fastapi.openapi.utils import get_openapi
from src.utils.openapi_fix import fix_openapi_spec

# ==================== INICIALIZAÇÃO DO FASTAPI ====================
app = FastAPI(
    title="Central de Atendimento Automática",
    description="API para gerenciar atendimento multicanal com IA e automação. Acesso protegido por autenticação JWT.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,  # Adiciona o gerenciador de ciclo de vida
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version="3.0.3",
        description=app.description,
        routes=app.routes,
    )

    # Corrige a especificação para ser compatível com OpenAPI 3.0.3
    fix_openapi_spec(openapi_schema)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# ==================== CORS ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Para dev. Em produção, especifique domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== ROTAS ====================


@app.get("/", tags=["Health"])
async def health_check():
    """Health check da API"""
    return {
        "status": "ok",
        "servico": "Central de Atendimento Automática",
        "versao": "1.0.0",
        "ambiente": "Azure App Service",
    }


@app.get("/health", tags=["Health"])
async def health():
    """Health check simples para Azure"""
    return {"status": "healthy"}


# ==================== REGISTRO DE ROTAS ====================
app.include_router(auth_router)
app.include_router(clientes_router)
app.include_router(chamados_router)
app.include_router(metricas_router)


# ==================== TRATAMENTO DE ERROS ====================
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Erro não tratado: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"erro": "Erro interno do servidor", "detalhes": str(exc)},
    )


# ==================== ENTRYPOINT ====================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
