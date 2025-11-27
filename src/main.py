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
from src.routes.boletos import router as boletos_router
from src.routes.chat import router as chat_router
from src.routes.dashboard import router as dashboard_router

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
    await init_db()  # Inicializa o banco de dados (Async)
    logger.info("✅ Banco de dados inicializado!")
    yield  # A aplicação roda aqui
    logger.info("🛑 Encerrando aplicação...")
    await close_db()  # Fecha as conexões com o banco de dados (Async)


from fastapi.openapi.utils import get_openapi
from src.utils.openapi_fix import fix_openapi_spec
from src.config.observability import setup_observability

# ==================== INICIALIZAÇÃO DO FASTAPI ====================
app = FastAPI(
    title="Central de Atendimento Automática",
    description="API para gerenciar atendimento multicanal com IA e automação. Acesso protegido por autenticação JWT.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,  # Adiciona o gerenciador de ciclo de vida
)

setup_observability(app)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version="3.0.1",
        description=app.description,
        routes=app.routes,
    )

    # Adiciona configuração de servidores se não existir
    if "servers" not in openapi_schema:
        openapi_schema["servers"] = [{"url": "/"}]

    # Corrige a especificação para ser compatível com OpenAPI 3.0.1
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
# ==================== REGISTRO DE ROTAS ====================
app.include_router(auth_router, prefix="/api")
app.include_router(clientes_router, prefix="/api")
app.include_router(chamados_router, prefix="/api")
app.include_router(metricas_router, prefix="/api")
app.include_router(boletos_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")


# ==================== STATIC FILES (FRONTEND) ====================
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount assets folder (JS, CSS, Images)
# Verifica se a pasta existe para evitar erros em dev local sem build
if os.path.exists("frontend/dist/assets"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

# Catch-all route for SPA (React Router)
# Deve ser a ÚLTIMA rota definida para não conflitar com a API
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # Se for uma chamada de API que não casou com nada acima, retorna 404 da API
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc"):
        return JSONResponse(status_code=404, content={"message": "Endpoint não encontrado"})

    # Para qualquer outra rota, serve o index.html do React
    # O React Router vai lidar com a rota no lado do cliente
    if os.path.exists("frontend/dist/index.html"):
        return FileResponse("frontend/dist/index.html")
    
    return {"message": "Frontend não encontrado. Execute 'npm run build' na pasta frontend."}


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
