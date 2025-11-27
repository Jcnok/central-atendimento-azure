# Master Prompt: Recreação do Projeto "central-atendimento-azure"

**Seu Papel:** Você é um agente de IA especialista em engenharia de software. Sua tarefa é seguir este roteiro para recriar um projeto completo a partir do zero.

**Sua Missão:** Recriar o projeto FastAPI "central-atendimento-azure" em sua totalidade, incluindo todo o código-fonte, testes, documentação, arquivos Docker e configuração de CI/CD. Siga cada passo precisamente, criando os arquivos com o conteúdo exato fornecido. Não faça commit ou push até que seja instruído.

---

## Passo 1: Criar a Estrutura de Diretórios

Execute o seguinte comando para criar a estrutura de pastas inicial:

```bash
mkdir -p src/config src/models src/schemas src/routes src/services src/utils tests .github/workflows
```

---

## Passo 2: Criar os Arquivos do Projeto

Crie cada um dos seguintes arquivos com o conteúdo exato fornecido.

### Arquivo: `pyproject.toml`

```toml
[tool.black]
line-length = 88
target-version = ['py310']

[tool.ruff]
line-length = 88

[tool.ruff.lint]
# Habilita as regras do Flake8 (F) e isort (I)
select = ["F", "I"]
ignore = []

[tool.ruff.format]
quote-style = "double"
```

### Arquivo: `requirements.in`

```
# Framework e Servidores
fastapi
gunicorn
uvicorn
python-multipart

# Banco de Dados
ssqlalchemy
psycopg2-binary

# Validação e Configuração
pydantic
pydantic-settings
email-validator
python-dotenv

# Autenticação e Segurança
python-jose[cryptography]
passlib==1.7.4
bcrypt==3.2.0

# Testes
pytest
pytest-asyncio
httpx
```

### Arquivo: `.gitignore`

```
# ==================== SEGURANÇA ====================
.env
.env.local
.env.*.local
.env.production
secrets.json
config.json
*.key
*.pem
*.pfx

# ==================== CREDENCIAIS ====================
credentials/
keys/
secrets/
.aws/
.azure/
.gcp/

# ==================== Python ====================
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# ==================== Virtual Environment ====================
virtualenv/
ENV/
env/
.venv
env.bak/
virtualenv.bak/

# ==================== IDE ====================
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
*.sublime-project
*.sublime-workspace

# ==================== Database ====================
db/*.db
db/*.sqlite
db/*.sqlite3
*.db
*.sqlite
*.sqlite3

# ==================== Pytest ====================
.pytest_cache/
.coverage
htmlcov/
.tox/
dist/

# ==================== Logs ====================
*.log
logs/
*.log.*

# ==================== OS ====================
.DS_Store
Thumbs.db
.directory

# ==================== Deployment ====================
deploy.zip
*.zip
*.tar.gz

# ==================== Node (se usar frontend) ====================
node_modules/
.npm
package-lock.json
yarn.lock

# ==================== Misc ====================
.cache/
.tmp/
.env.test
```

### Arquivo: `.env.example`

```
# ==================== DOCKER & POSTGRES (para docker-compose) ====================
# Credenciais para o container do banco de dados PostgreSQL
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_DB=central_atendimento_db

# ==================== DATABASE ====================
# String de conexão com o banco de dados.
# Escolha UMA das opções abaixo, dependendo do seu ambiente.

# Opção 1: Para desenvolvimento local (sem Docker) ou produção (Azure)
# DATABASE_URL=postgresql://user:password@host:port/database

# Opção 2: Para desenvolvimento com Docker Compose
# O host 'db' refere-se ao nome do serviço do banco de dados no docker-compose.yml
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}


# ==================== APLICAÇÃO ====================
APP_ENV=development
APP_DEBUG=False
APP_HOST=0.0.0.0
APP_PORT=8000

# ==================== AZURE (Opcional) ====================
# Para integração com Azure Cognitive Services no futuro
AZURE_COGNITIVE_KEY=sua_chave_aqui
AZURE_COGNITIVE_ENDPOINT=https://seu-endpoint.cognitiveservices.azure.com/

# ==================== LOGGING ====================
LOG_LEVEL=INFO

# ==================== AUTHENTICATION ====================
# Chave secreta para assinar os tokens JWT.
# **MUITO IMPORTANTE**: Use uma chave forte e aleatória em produção.
# Gerar com: openssl rand -hex 32
SECRET_KEY=sua_chave_secreta_aqui_gerada_aleatoriamente

# Algoritmo de assinatura do token JWT (padrão: HS256)
ALGORITHM=HS256

# Tempo de expiração do token de acesso em minutos (padrão: 30)
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Arquivo: `src/main.py`

```python
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


# ==================== INICIALIZAÇÃO DO FASTAPI ====================
app = FastAPI(
    title="Central de Atendimento Automática",
    description="API para gerenciar atendimento multicanal com IA e automação. Acesso protegido por autenticação JWT.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,  # Adiciona o gerenciador de ciclo de vida
)

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
```

### Arquivo: `src/config/settings.py`

```python
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

    # ==================== JWT ====================
    SECRET_KEY: str = Field(..., description="Chave secreta para assinar os tokens JWT.")
    ALGORITHM: str = Field("HS256", description="Algoritmo de assinatura do token JWT.")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        30, description="Tempo de expiração do token de acesso em minutos."
    )


# Instância única das configurações para ser importada em outros módulos
try:
    settings = Settings()
    logger.info("✅ Configurações da aplicação carregadas com sucesso.")
except Exception as e:
    logger.error(f"❌ Erro ao carregar as configurações: {e}")
    raise
```

### Arquivo: `src/config/database.py`

```python
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
```

### Arquivo: `src/models/user.py`

```python
from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy.orm import relationship
from src.config.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    chamados = relationship("Chamado", back_populates="user")
```

### Arquivo: `src/models/cliente.py`

```python
from sqlalchemy import Column, DateTime, Integer, String, func

from src.config.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    telefone = Column(String(20))
    canal_preferido = Column(String(50), default="site")
    data_criacao = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Cliente(id={self.id}, email={self.email})>"
```

### Arquivo: `src/models/chamado.py`

```python
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship
from src.config.database import Base


class Chamado(Base):
    __tablename__ = "chamados"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    canal = Column(String(50), nullable=False)  # "site", "whatsapp", "email"
    mensagem = Column(Text, nullable=False)
    status = Column(
        String(50), default="aberto"  # "aberto", "resolvido", "encaminhado"
    )
    resposta_automatica = Column(Text)
    encaminhado_para_humano = Column(Boolean, default=False)
    data_criacao = Column(DateTime, server_default=func.now())
    data_atualizacao = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="chamados")

    def __repr__(self):
        return f"<Chamado(id={self.id}, cliente_id={self.cliente_id}, status={self.status})>"
```

### Arquivo: `src/models/metrica.py`

```python
from sqlalchemy import Column, DateTime, Float, Integer, func

from src.config.database import Base


class Metrica(Base):
    __tablename__ = "metricas"

    id = Column(Integer, primary_key=True, index=True)
    total_chamados = Column(Integer, default=0)
    chamados_automaticos = Column(Integer, default=0)
    chamados_encaminhados = Column(Integer, default=0)
    tempo_medio_resposta = Column(Float, default=0.0)
    data_atualizacao = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Metrica(id={self.id}, total={self.total_chamados})>"
```

### Arquivo: `src/schemas/user.py`

```python
from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserSchema(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    username: str
    password: str
```

### Arquivo: `src/schemas/cliente.py`

```python
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class ClienteCreate(BaseModel):
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    canal_preferido: str = "site"


class ClienteResponse(BaseModel):
    id: int
    nome: str
    email: str
    telefone: Optional[str]
    canal_preferido: str
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)
```

### Arquivo: `src/schemas/chamado.py`

```python
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ChamadoCreate(BaseModel):
    cliente_id: int
    canal: str
    mensagem: str


class ChamadoResponse(BaseModel):
    id: int
    cliente_id: int
    canal: str
    mensagem: str
    status: str
    resposta_automatica: Optional[str]
    encaminhado_para_humano: bool
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)


class ChamadoCreateResponse(BaseModel):
    """Schema de resposta para a criação de um novo chamado."""

    chamado_id: int
    cliente_id: int
    canal: str
    resposta: str
    resolvido_automaticamente: bool
    prioridade: str
    encaminhado_para_humano: bool
    data_criacao: datetime
```

### Arquivo: `src/utils/security.py`

```python
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.config.settings import settings
from src.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    username: Optional[str] = None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user
```

### Arquivo: `src/routes/auth.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.models.user import User
from src.schemas.user import UserCreate
from src.utils.security import create_access_token, get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
```

### Arquivo: `src/routes/clientes.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.models.cliente import Cliente
from src.schemas.cliente import ClienteCreate, ClienteResponse
from src.utils.security import get_current_user

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post(
    "/",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """Cria um novo cliente"""
    try:
        novo_cliente = Cliente(
            nome=cliente.nome,
            email=cliente.email,
            telefone=cliente.telefone,
            canal_preferido=cliente.canal_preferido,
        )
        db.add(novo_cliente)
        db.commit()
        db.refresh(novo_cliente)
        return novo_cliente
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado"
        )


@router.get(
    "/{cliente_id}",
    response_model=ClienteResponse,
    dependencies=[Depends(get_current_user)],
)
def obter_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Obtém informações de um cliente"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado"
        )
    return cliente


@router.get(
    "/",
    response_model=list[ClienteResponse],
    dependencies=[Depends(get_current_user)],
)
def listar_clientes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Lista todos os clientes"""
    return db.query(Cliente).offset(skip).limit(limit).all()
```

### Arquivo: `src/routes/chamados.py`

```python
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.models.chamado import Chamado
from src.models.cliente import Cliente
from src.schemas.chamado import (
    ChamadoCreate,
    ChamadoCreateResponse,
    ChamadoResponse,
)
from src.services.ia_classifier import IAClassifier
from src.utils.security import get_current_user

router = APIRouter(prefix="/chamados", tags=["Chamados"])


@router.post(
    "/",
    response_model=ChamadoCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_chamado(
    chamado: ChamadoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Cria um novo chamado (ticket de atendimento)
    Automaticamente classifica com IA e decide se resolve ou encaminha
    """
    # Verifica se cliente existe
    cliente = db.query(Cliente).filter(Cliente.id == chamado.cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado"
        )

    # Classifica a mensagem com IA
    classificacao = IAClassifier.classificar(chamado.mensagem, chamado.canal)

    # Cria o chamado no banco
    novo_chamado = Chamado(
        cliente_id=chamado.cliente_id,
        user_id=current_user.id,
        canal=chamado.canal,
        mensagem=chamado.mensagem,
        status="resolvido" if classificacao["resolvido"] else "aberto",
        resposta_automatica=classificacao["resposta"],
        encaminhado_para_humano=not classificacao["resolvido"],
    )

    db.add(novo_chamado)
    db.commit()
    db.refresh(novo_chamado)

    return ChamadoCreateResponse(
        chamado_id=novo_chamado.id,
        cliente_id=novo_chamado.cliente_id,
        canal=novo_chamado.canal,
        resposta=classificacao["resposta"],
        resolvido_automaticamente=classificacao["resolvido"],
        prioridade=classificacao["prioridade"],
        encaminhado_para_humano=not classificacao["resolvido"],
        data_criacao=novo_chamado.data_criacao,
    )


@router.get(
    "/{chamado_id}",
    response_model=ChamadoResponse,
    dependencies=[Depends(get_current_user)],
)
def obter_chamado(chamado_id: int, db: Session = Depends(get_db)):
    """Obtém informações de um chamado específico"""
    chamado = db.query(Chamado).filter(Chamado.id == chamado_id).first()
    if not chamado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chamado não encontrado"
        )
    return chamado


@router.get(
    "/",
    response_model=list[ChamadoResponse],
    dependencies=[Depends(get_current_user)],
)
def listar_chamados(
    status_filtro: str = None,
    canal: str = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    Lista chamados com filtros opcionais
    Filtros: status (aberto, resolvido, encaminhado), canal (site, whatsapp, email)
    """
    query = db.query(Chamado)

    if status_filtro:
        query = query.filter(Chamado.status == status_filtro)

    if canal:
        query = query.filter(Chamado.canal == canal)

    chamados = (
        query.order_by(desc(Chamado.data_criacao)).offset(skip).limit(limit).all()
    )
    return chamados


@router.put(
    "/{chamado_id}",
    response_model=ChamadoResponse,
    dependencies=[Depends(get_current_user)],
)
def atualizar_chamado_status(
    chamado_id: int, novo_status: str, db: Session = Depends(get_db)
):
    """Atualiza o status de um chamado"""
    chamado = db.query(Chamado).filter(Chamado.id == chamado_id).first()
    if not chamado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chamado não encontrado"
        )

    status_validos = ["aberto", "resolvido", "encaminhado"]
    if novo_status not in status_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status inválido. Deve ser um de: {status_validos}",
        )

    chamado.status = novo_status
    chamado.data_atualizacao = datetime.now()
    db.commit()
    db.refresh(chamado)

    return chamado


@router.get(
    "/cliente/{cliente_id}",
    response_model=list[ChamadoResponse],
    dependencies=[Depends(get_current_user)],
)
def listar_chamados_por_cliente(
    cliente_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """Lista todos os chamados de um cliente específico"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado"
        )

    chamados = (
        db.query(Chamado)
        .filter(Chamado.cliente_id == cliente_id)
        .order_by(desc(Chamado.data_criacao))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return chamados
```

### Arquivo: `src/routes/metricas.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.models.chamado import Chamado
from src.models.cliente import Cliente
from src.utils.security import get_current_user

router = APIRouter(prefix="/metricas", tags=["Métricas"])


@router.get("/", response_model=dict, dependencies=[Depends(get_current_user)])
def obter_metricas(db: Session = Depends(get_db)):
    """Retorna métricas gerais de atendimento"""

    total_chamados = db.query(func.count(Chamado.id)).scalar() or 0
    chamados_automaticos = (
        db.query(func.count(Chamado.id))
        .filter(Chamado.encaminhado_para_humano == False)
        .scalar()
        or 0
    )
    chamados_encaminhados = (
        db.query(func.count(Chamado.id))
        .filter(Chamado.encaminhado_para_humano == True)
        .scalar()
        or 0
    )

    total_clientes = db.query(func.count(Cliente.id)).scalar() or 0

    taxa_resolucao = (
        (chamados_automaticos / total_chamados * 100) if total_chamados > 0 else 0
    )

    return {
        "total_chamados": total_chamados,
        "total_clientes": total_clientes,
        "chamados_resolvidos_automaticamente": chamados_automaticos,
        "chamados_encaminhados_para_humano": chamados_encaminhados,
        "taxa_resolucao_automatica": f"{taxa_resolucao:.1f}%",
        "tempo_medio_resposta_segundos": "< 1s (mock)",
    }


@router.get(
    "/por-canal", response_model=dict, dependencies=[Depends(get_current_user)]
)
def metricas_por_canal(db: Session = Depends(get_db)):
    """Retorna métricas detalhadas por canal"""
    canais = ["site", "whatsapp", "email"]
    resultado = {}

    for canal in canais:
        total = (
            db.query(func.count(Chamado.id)).filter(Chamado.canal == canal).scalar()
            or 0
        )
        automaticos = (
            db.query(func.count(Chamado.id))
            .filter(Chamado.canal == canal, Chamado.encaminhado_para_humano == False)
            .scalar()
            or 0
        )

        resultado[canal] = {
            "total": total,
            "resolvidos_automaticamente": automaticos,
            "taxa_resolucao": f"{(automaticos/total*100):.1f}%" if total > 0 else "0%",
        }

    return resultado


@router.get(
    "/por-status", response_model=dict, dependencies=[Depends(get_current_user)]
)
def metricas_por_status(db: Session = Depends(get_db)):
    """Retorna distribuição de chamados por status"""
    statuses = ["aberto", "resolvido", "encaminhado"]
    resultado = {}

    for status in statuses:
        count = (
            db.query(func.count(Chamado.id)).filter(Chamado.status == status).scalar()
            or 0
        )
        resultado[status] = count

    return resultado
```

### Arquivo: `src/services/ia_classifier.py`

```python
"""
Serviço de classificação e resposta automática com IA (mock)
Aqui você integra com Azure Cognitive Services, N8N, ou LLM de sua escolha
"""


class IAClassifier:
    @staticmethod
    def classificar(mensagem: str, canal: str) -> dict:
        """
        Classifica a mensagem e decide se pode resolver automaticamente
        """
        mensagem_lower = mensagem.lower()

        # Classificação baseada em palavras-chave
        if any(
            palavra in mensagem_lower
            for palavra in ["segunda via", "boleto", "fatura", "invoice"]
        ):
            return {
                "intencao": "documento",
                "resposta": "📄 Clique aqui para acessar suas faturas e segunda via de boletos.",
                "resolvido": True,
                "prioridade": "baixa",
            }

        elif any(
            palavra in mensagem_lower
            for palavra in ["meu plano", "upgrade", "downgrade", "trocar plano"]
        ):
            return {
                "intencao": "gerenciamento_plano",
                "resposta": "📋 Para gerenciar seu plano, acesse 'Minha Conta' no menu principal.",
                "resolvido": True,
                "prioridade": "média",
            }

        elif any(
            palavra in mensagem_lower
            for palavra in [
                "problema",
                "erro",
                "não funciona",
                "bugado",
                "travado",
                "urgente",
            ]
        ):
            return {
                "intencao": "problema_tecnico",
                "resposta": "⚠️ Seu chamado foi registrado como prioritário. Um especialista entrará em contato em breve.",
                "resolvido": False,
                "prioridade": "alta",
            }

        elif any(
            palavra in mensagem_lower
            for palavra in ["obrigado", "valeu", "thanks", "tks"]
        ):
            return {
                "intencao": "agradecimento",
                "resposta": "😊 De nada! Fico feliz em ajudar. Qualquer dúvida, estarei aqui.",
                "resolvido": True,
                "prioridade": "baixa",
            }

        else:
            return {
                "intencao": "geral",
                "resposta": "👋 Obrigado pelo contato! Seu chamado foi registrado. Responderemos em breve.",
                "resolvido": False,
                "prioridade": "média",
            }
```

### Arquivo: `tests/conftest.py`

```python
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.config.database import Base, get_db
from src.main import app

# ================== CONFIGURAÇÃO DO BANCO DE DADOS DE TESTE ==================

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ================== SOBRESCRITA DA DEPENDÊNCIA DO BANCO ==================


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ================== FIXTURE DE SETUP DO BANCO ==================


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


@pytest.fixture(scope="function")
def auth_token(db_session):
    """
    Fixture that creates a user, logs in, and returns an auth token.
    Depends on db_session to ensure tables are created.
    """
    unique_username = f"testuser_{uuid.uuid4().hex}"
    unique_email = f"test_{uuid.uuid4().hex}@example.com"

    signup_response = client.post(
        "/auth/signup",
        json={
            "username": unique_username,
            "email": unique_email,
            "password": "password",
        },
    )
    assert signup_response.status_code == 200, f"Signup failed: {signup_response.text}"

    login_response = client.post(
        "/auth/login",
        data={"username": unique_username, "password": "password"},
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"

    token = login_response.json().get("access_token")
    assert token is not None
    return token
```

### Arquivo: `tests/test_auth_endpoints.py`

```python
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestAuthEndpoints:
    def test_signup(self, db_session):
        response = client.post(
            "/auth/signup",
            json={"username": "testuser", "email": "test@example.com", "password": "password"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login(self, db_session):
        client.post(
            "/auth/signup",
            json={"username": "testuser2", "email": "test2@example.com", "password": "password"},
        )
        response = client.post(
            "/auth/login",
            data={"username": "testuser2", "password": "password"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_access_protected_endpoint(self, db_session):
        # Use the db_session fixture to ensure the database is initialized
        response = client.post(
            "/auth/signup",
            json={"username": "testuser3", "email": "test3@example.com", "password": "password"},
        )
        assert response.status_code == 200
        access_token = response.json()["access_token"]
        response = client.get(
            "/clientes/", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
```

### Arquivo: `tests/test_endpoints.py`

```python
"""
Testes automatizados dos endpoints da API FastAPI.
Estes testes rodam em um banco de dados SQLite em memória para garantir
isolamento, segurança e velocidade.
"""

import uuid

from fastapi.testclient import TestClient

from src.main import app
from src.models.chamado import Chamado

client = TestClient(app)


# ================== CLASSES DE TESTE ==================


class TestHealthCheck:
    def test_health_check_root(self, db_session):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_check_health(self, db_session):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestClientes:
    def test_criar_cliente(self, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        email_unico = f"joao_{uuid.uuid4().hex}@example.com"
        response = client.post(
            "/clientes/",
            json={
                "nome": "João Silva",
                "email": email_unico,
                "telefone": "11999999999",
                "canal_preferido": "whatsapp",
            },
            headers=headers,
        )
        assert response.status_code == 201
        assert isinstance(response.json()["id"], int)

    def test_obter_cliente(self, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        email_unico = f"maria_{uuid.uuid4().hex}@example.com"
        response_create = client.post(
            "/clientes/",
            json={
                "nome": "Maria Silva",
                "email": email_unico,
                "telefone": "11988888888",
            },
            headers=headers,
        )
        cliente_id = response_create.json()["id"]
        response = client.get(f"/clientes/{cliente_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["nome"] == "Maria Silva"

    def test_listar_clientes(self, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/clientes/", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_criar_cliente_email_duplicado(self, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        email_unico = f"duplicado_{uuid.uuid4().hex}@example.com"
        client.post(
            "/clientes/",
            json={
                "nome": "Cliente Duplicado",
                "email": email_unico,
                "telefone": "11977777777",
            },
            headers=headers,
        )
        response = client.post(
            "/clientes/",
            json={
                "nome": "Cliente Duplicado 2",
                "email": email_unico,
                "telefone": "11977777778",
            },
            headers=headers,
        )
        assert response.status_code == 400


class TestChamados:
    def criar_cliente(self, headers):
        email_unico = f"clientechamado_{uuid.uuid4().hex}@example.com"
        response = client.post(
            "/clientes/",
            json={
                "nome": "Cliente Chamados",
                "email": email_unico,
                "telefone": "11999999999",
            },
            headers=headers,
        )
        return response.json()["id"]

    def test_criar_chamado_com_resolucao_automatica(self, auth_token, db_session):
        headers = {"Authorization": f"Bearer {auth_token}"}
        cliente_id = self.criar_cliente(headers)
        response = client.post(
            "/chamados/",
            json={
                "cliente_id": cliente_id,
                "canal": "site",
                "mensagem": "segunda via boleto",
            },
            headers=headers,
        )
        assert response.status_code == 201
        assert response.json()["resolvido_automaticamente"] is True
        assert "segunda via" in response.json()["resposta"].lower()

        chamado = db_session.get(Chamado, response.json()["chamado_id"])
        assert chamado.user_id is not None

    def test_criar_chamado_para_encaminhamento(self, auth_token, db_session):
        headers = {"Authorization": f"Bearer {auth_token}"}
        cliente_id = self.criar_cliente(headers)
        response = client.post(
            "/chamados/",
            json={
                "cliente_id": cliente_id,
                "canal": "whatsapp",
                "mensagem": "meu sistema está com erro grave",
            },
            headers=headers,
        )
        assert response.status_code == 201
        assert response.json()["resolvido_automaticamente"] is False
        assert response.json()["encaminhado_para_humano"] is True

        chamado = db_session.get(Chamado, response.json()["chamado_id"])
        assert chamado.user_id is not None

    def test_obter_chamado(self, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        cliente_id = self.criar_cliente(headers)
        create_response = client.post(
            "/chamados/",
            json={
                "cliente_id": cliente_id,
                "canal": "email",
                "mensagem": "qual meu plano?",
            },
            headers=headers,
        )
        chamado_id = create_response.json()["chamado_id"]
        response = client.get(f"/chamados/{chamado_id}", headers=headers)
        assert response.status_code == 200

    def test_listar_chamados(self, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/chamados/", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_listar_chamados_por_canal(self, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/chamados/?canal=site", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestMetricas:
    def test_obter_metricas_gerais(self, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/metricas/", headers=headers)
        assert response.status_code == 200
        assert "total_chamados" in response.json()
        assert "taxa_resolucao_automatica" in response.json()

    def test_metricas_por_canal(self, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/metricas/por-canal", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_metricas_por_status(self, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/metricas/por-status", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
```

### Arquivo: `startup.sh`

```bash
#!/bin/bash

# Script de inicialização para Azure App Service

echo "🚀 Iniciando Gunicorn para a aplicação FastAPI..."

# O Azure App Service injeta a porta na variável de ambiente $PORT.
# O Gunicorn deve escutar nesta porta para que a plataforma consiga
# rotear o tráfego corretamente para a aplicação.
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app --bind "0.0.0.0:$PORT"
```

### Arquivo: `reset_db.py`

```python
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
```

### Arquivo: `.dockerignore`

```
# Git
.git
.gitignore

# Docker
Dockerfile

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
virtualenv/
.venv/

# Cache
.pytest_cache/
.ruff_cache/

# IDEs
.vscode/
.idea/

# Arquivos de ambiente locais
.env
```

### Arquivo: `Dockerfile`

```dockerfile
# Usar uma imagem base oficial do Python. A versão 'slim' é mais leve.
FROM python:3.10-slim

# Definir variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Instalar dependências do sistema, se necessário (ex: para psycopg2)
# Neste caso, a imagem slim já contém o necessário, mas é uma boa prática deixar a linha comentada.
# RUN apt-get update && apt-get install -y ...

# Copiar o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar todo o código da aplicação para o diretório de trabalho
COPY . .

# Expor a porta que a aplicação irá rodar.
# O Gunicorn será configurado para usar a porta 8000.
EXPOSE 8000

# Comando para iniciar a aplicação quando o container for executado.
# Usamos Gunicorn para um ambiente de produção.
# O comando é o mesmo do startup.sh, mas sem a necessidade de especificar o bind,
# pois o docker-compose fará o mapeamento da porta.
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "src.main:app", "--bind", "0.0.0.0:8000"]
```

### Arquivo: `docker-compose.yml`

```yaml
version: '3.8'

services:
  # Serviço da API FastAPI
  api:
    build: .
    container_name: central_atendimento_api
    command: gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app --bind 0.0.0.0:8000
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src # Monta o código-fonte para live-reloading (opcional, bom para dev)
    env_file:
      - .env # Carrega as variáveis de ambiente do arquivo .env
    depends_on:
      db:
        condition: service_healthy # Espera o banco de dados estar saudável antes de iniciar a API
    restart: on-failure

  # Serviço do Banco de Dados PostgreSQL
  db:
    image: postgres:14-alpine
    container_name: central_atendimento_db
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    ports:
      - "5432:5432" # Expõe a porta do banco para o host (opcional, bom para debug)
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: always

volumes:
  postgres_data:
    driver: local
```

### Arquivo: `.github/workflows/deploy.yml`

```yaml
name: Deploy to Azure App Service

on:
  push:
    branches:
      - master # Ou 'main', dependendo do nome da sua branch principal

env:
  AZURE_WEBAPP_NAME: app-central-atendimento-19055 # Nome do seu App Service
  PYTHON_VERSION: '3.10' # Versão do Python usada no seu projeto

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python ${{ env.PYTHON_VERSION }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      run: |
        pytest
      env:
        DATABASE_URL: "postgresql://test:test@localhost/testdb"
        SECRET_KEY: "test_secret_key_for_ci"

    - name: Log in to Azure
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}

    - name: Deploy to Azure Web App
      uses: azure/webapps-deploy@v2
      with:
        app-name: ${{ env.AZURE_WEBAPP_NAME }}
        slot-name: 'production'
        package: . # Implanta o conteúdo do diretório raiz do repositório
        startup-command: 'gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app'
```

### Arquivo: `README.md`

```markdown
# 🎯 Central de Atendimento Automática com IA

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-green?logo=fastapi)
[![Deploy to Azure App Service](https://github.com/Jcnok/central-atendimento-azure/actions/workflows/deploy.yml/badge.svg)](https://github.com/Jcnok/central-atendimento-azure/actions)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg?logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Uma API de back-end robusta para uma central de atendimento, capaz de processar solicitações de múltiplos canais com classificação e resposta por IA.

**Desenvolvido para o Hackathon Microsoft Innovation Challenge - Novembro 2025**

---

## 📋 Sumário
- [Visão Geral](#-visão-geral)
- [Tecnologias](#-tecnologias)
- [Arquitetura](#-arquitetura)
- [🚀 Começando: Guia de Instalação](#-começando-guia-de-instalação)
- [🐳 Rodando com Docker Compose](#-rodando-com-docker-compose)
- [⚙️ Variáveis de Ambiente](#-variáveis-de-ambiente)
- [📡 Testando a API: Guia Prático](#-testando-a-api-guia-prático)
- [☁️ Deploy e CI/CD na Azure](#-deploy-e-cicd-na-azure)
- [🤔 Solução de Problemas (Troubleshooting)](#-solução-de-problemas-troubleshooting)
- [🧪 Testes Automatizados](#-testes-automatizados)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [📈 Roadmap](#-roadmap)
- [📝 Licença e Contato](#-licença-e-contato)

---

## 🌟 Visão Geral

Este projeto oferece uma solução escalável para empresas que lidam com um alto volume de solicitações de clientes em diversos canais (site, WhatsApp, e-mail).

#### O Problema

-   Processamento manual e lento de solicitações.
-   Dificuldade em oferecer suporte 24/7.
-   Custos operacionais elevados com atendimento humano para dúvidas repetitivas.

#### A Solução

Um orquestrador de atendimento que automatiza o fluxo de trabalho:
-   ✅ **Recebe** solicitações de múltiplos canais.
-   ✅ **Classifica** a intenção do cliente com IA em tempo real.
-   ✅ **Responde** automaticamente a dúvidas frequentes (ex: segunda via de boleto).
-   ✅ **Encaminha** casos complexos e priorizados para análise humana.
-   ✅ **Gera métricas** sobre os atendimentos para análise de performance.

---


## 🛠️ Tecnologias

| Área | Tecnologia | Versão/Descrição |
| :--- | :--- | :--- |
| **Linguagem** | Python | 3.10+ |
| **Framework Web** | FastAPI | ASGI, alta performance |
| **Banco de Dados** | PostgreSQL | Banco de dados relacional |
| **ORM** | SQLAlchemy | v2.0, para manipulação de dados segura|
| **Validação**| Pydantic | v2, para validação e configurações |
| **Containerização** | Docker / Docker Compose | Ambiente de desenvolvimento padronizado. |
| **Servidor** | Uvicorn & Gunicorn| Servidores ASGI/WSGI para dev/prod |
| **Testes** | Pytest | Testes automatizados com BD em memória |
| **Cloud** | Azure App Service | Hospedagem da aplicação |
| **CI/CD** | GitHub Actions | Automação de testes e deploy. |

---

## 🏗️ Arquitetura

A arquitetura segue um padrão de camadas desacoplado, facilitando a manutenção e a escalabilidade.

```
┌──────────────────────────────────┐
│         Canais de Entrada        │
│    (Frontend, WhatsApp, etc.)    │
└──────────────┬───────────────────┘
               │ HTTP POST
               ▼
┌──────────────────────────────────┐
│     Azure App Service (FastAPI)  │
│     - API Gateway                │
│     - Lógica de Negócio          │
└──────────────┬───────────────────┘
      ┌────────┴─────────┐
      ▼                  ▼
┌────────────────┐   ┌─────────────────┐
│ IA Classifier  │   │   PostgreSQL DB │
│ (Classificação)│   │  (Azure/Local)  │
└────────────────┘   └─────────────────┘
```
---


## 🚀 Começando: Guia de Instalação

Siga os passos abaixo para ter o projeto rodando localmente **sem Docker**.

#### 1. Pré-requisitos

-   [Python 3.10+](https://www.python.org/)
-   [Git](https://git-scm.com/)
-   Um servidor PostgreSQL rodando (localmente ou na nuvem).

#### 2. Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/Jcnok/central-atendimento-azure.git
cd central-atendimento-azure

# 2. Crie e ative um ambiente virtual
# No Linux/macOS
python3 -m venv venv
source venv/bin/activate

# No Windows
python -m venv venv
virtualenv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt
```

#### 3. Configuração do Ambiente

A aplicação precisa de variáveis de ambiente para rodar.

```bash
# Copie o arquivo de exemplo. Este será seu arquivo de configuração local.
cp .env.example .env
```
Agora, **abra o arquivo `.env`** e preencha as variáveis obrigatórias. Para o setup local, você precisará da `DATABASE_URL` apontando para seu banco de dados local e de uma `SECRET_KEY`.

#### 4. Execução

Com tudo configurado, inicie a aplicação:
```bash
# Inicie o servidor em modo de desenvolvimento com auto-reload
uvicorn src.main:app --reload
```
A API estará disponível em `http://127.0.0.1:8000`.

---


## 🐳 Rodando com Docker Compose

Esta é a forma **recomendada e mais simples** para rodar o ambiente de desenvolvimento. O Docker Compose irá orquestrar a API e o banco de dados automaticamente.

### 1. Pré-requisitos
- [Docker](https://www.docker.com/products/docker-desktop/) e Docker Compose instalados.

### 2. Configuração
```bash
# 1. Clone o repositório (se ainda não o fez)
git clone https://github.com/Jcnok/central-atendimento-azure.git
cd central-atendimento-azure

# 2. Crie seu arquivo de ambiente a partir do exemplo
cp .env.example .env
```
**Nenhuma alteração é necessária no arquivo `.env` para o Docker Compose funcionar**, pois ele já vem pré-configurado para o ambiente Docker.

### 3. Execução
```bash
# Suba os containers da API e do banco de dados em modo "detached" (-d)
docker-compose up --build -d
```
- O comando `--build` garante que a imagem da sua API será reconstruída se houver alterações no `Dockerfile` ou no código-fonte.
- O `-d` faz com que os containers rodem em segundo plano.

A API estará disponível em `http://127.0.0.1:8000`.

### Comandos Úteis do Docker Compose
- **Parar os containers**: `docker-compose down`
- **Ver os logs da API**: `docker-compose logs -f api`
- **Acessar o shell dentro do container da API**: `docker-compose exec api bash`

---


## ⚙️ Variáveis de Ambiente

As configurações são carregadas do arquivo `.env`.

| Variável | Obrigatório? | Descrição | Exemplo |
| :--- | :---: | :--- | :--- |
| `DATABASE_URL` | **Sim** | String de conexão com o PostgreSQL. | `postgresql://user:pass@host:port/db` |
| `SECRET_KEY` | **Sim** | Chave secreta para assinar os tokens JWT. | `uma_chave_super_secreta_e_segura` |
| `ALGORITHM` | Não | Algoritmo de assinatura do token JWT. | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Não | Tempo de expiração do token de acesso. | `30` |
| `POSTGRES_USER` | **Sim** (Docker) | Usuário do banco de dados para o container. | `admin` |
| `POSTGRES_PASSWORD` | **Sim** (Docker) | Senha do banco de dados para o container. | `admin` |
| `POSTGRES_DB` | **Sim** (Docker) | Nome do banco de dados a ser criado. | `central_atendimento_db` |

<details>
<summary><strong>Dica de Segurança para a SECRET_KEY</strong></summary>

Nunca use chaves fracas ou exemplos em produção. Para gerar uma chave forte e aleatória, use o seguinte comando no seu terminal e copie o resultado para a sua variável `SECRET_KEY` no arquivo `.env`:

```bash
openssl rand -hex 32
```
</details>

---


## 📡 Testando a API: Guia Prático

Para interagir com os endpoints, especialmente os protegidos, siga este guia passo a passo usando a documentação interativa do Swagger UI.

1.  **Acesse a Documentação**
    -   Com a aplicação rodando, abra o seu navegador em: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

2.  **Crie uma Conta de Usuário**
    -   Vá até o endpoint `POST /auth/signup`.
    -   Clique em "Try it out".
    -   Preencha o `username`, `email` e `password` no corpo da requisição e clique em "Execute".
    -   Você deve receber uma resposta com um `access_token`. **Você não precisa copiar este token inicial**.

3.  **Autorize sua Sessão no Swagger UI**
    -   No topo da página, clique no botão verde **"Authorize"**.
    -   Uma janela pop-up chamada "Available authorizations" aparecerá.
    -   No formulário, digite o `username` e `password` que você acabou de criar.
    -   **Ignore os campos `client_id` e `client_secret`**. Eles não são usados neste projeto.
    -   Clique no botão azul **"Authorize"** na parte inferior da janela.
    -   Pode fechar a janela (botão "Close"). Agora você verá um ícone de cadeado fechado, indicando que sua sessão está autenticada.

4.  **Teste um Endpoint Protegido**
    -   Agora você pode testar qualquer endpoint protegido, como `POST /clientes/`.
    -   Clique em "Try it out", preencha os dados de um cliente e clique em "Execute".
    -   A requisição agora será enviada com o cabeçalho de autorização correto, e você deve receber uma resposta `201 Created`.

---


## ☁️ Deploy e CI/CD na Azure

Este guia descreve o processo completo para fazer o deploy da aplicação na Azure com um pipeline de CI/CD automatizado usando GitHub Actions.

### Visão Geral do Processo
1.  **Provisionar Recursos na Azure**: Criar a infraestrutura na nuvem (Banco de Dados e App Service).
2.  **Configurar a Conexão Segura**: Criar um Service Principal para permitir que o GitHub se autentique no Azure.
3.  **Configurar o Pipeline**: Apontar o workflow do GitHub Actions para os recursos criados.
4.  **Configurar a Aplicação na Azure**: Adicionar as variáveis de ambiente no App Service.
5.  **Ativar o Pipeline**: Fazer um `push` para a branch `master` para iniciar o deploy.

### Passo 1: Provisionar Recursos na Azure (CLI)

A forma mais rápida de criar os recursos necessários é via Azure CLI.

```bash
# Faça o login na sua conta Azure
az login

# --- CRIE O GRUPO DE RECURSOS E O BANCO DE DADOS ---
# Defina as variáveis para seus recursos
RESOURCE_GROUP="central-atendimento-rg"
LOCATION="canadacentral"
POSTGRES_SERVER_NAME="pg-central-atendimento-$RANDOM"
POSTGRES_DB_NAME="central_atendimento_db"
ADMIN_USER="dbadmin"
ADMIN_PASSWORD="SuaSenhaSuperForte123!" # ATENÇÃO: Use uma senha forte e segura!

# Crie o grupo de recursos
az group create --name $RESOURCE_GROUP --location $LOCATION

# Crie o servidor PostgreSQL Flexível
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name $POSTGRES_SERVER_NAME \
  --location $LOCATION \
  --admin-user $ADMIN_USER \
  --admin-password $ADMIN_PASSWORD \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --public-access 0.0.0.0 \
  --storage-size 32 \
  --version 14

# Crie o banco de dados dentro do servidor
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $POSTGRES_SERVER_NAME \
  --database-name $POSTGRES_DB_NAME

# --- CRIE O APP SERVICE ---
# Defina um nome único para sua aplicação web
WEBAPP_NAME="app-central-atendimento-$RANDOM"

# Registre o provedor de recursos da web (necessário apenas uma vez por assinatura)
az provider register --namespace Microsoft.Web

# Crie o App Service
az webapp up \
  --resource-group $RESOURCE_GROUP \
  --name $WEBAPP_NAME \
  --sku B1 \
  --location $LOCATION

# Anote o nome do seu Web App (WEBAPP_NAME) e a string de conexão do banco de dados.
# Você precisará deles nos próximos passos.
```

### Passo 2: Configurar a Conexão Segura (GitHub <> Azure)

1.  **Crie um Service Principal**: Esta é a identidade que o GitHub usará para se autenticar. Substitua `{seu-subscription-id}` e `{seu-grupo-de-recursos}` pelos seus valores.
    ```bash
    # Obtenha seu ID de assinatura
    az account show --query id --output tsv

    # Crie o Service Principal com escopo para o seu grupo de recursos
    az ad sp create-for-rbac \
      --name "sp-central-atendimento-github" \
      --role "contributor" \
      --scopes "/subscriptions/{seu-subscription-id}/resourceGroups/{seu-grupo-de-recursos}" \
      --sdk-auth
    ```
2.  **Copie o JSON de Saída**: O comando acima irá gerar um bloco de código JSON. Copie-o inteiramente.
3.  **Crie um Segredo no GitHub**:
    -   Vá para o seu repositório no GitHub: **Settings > Secrets and variables > Actions**.
    -   Clique em **New repository secret**.
    -   **Name**: `AZURE_CREDENTIALS`
    -   **Secret**: Cole o JSON copiado.
    -   Clique em **Add secret**.

### Passo 3: Configurar o Pipeline de CI/CD

O pipeline já está definido em `.github/workflows/deploy.yml`. Você só precisa ajustá-lo para apontar para o seu App Service.

1.  Abra o arquivo `.github/workflows/deploy.yml`.
2.  Encontre a seção `env` e altere o valor de `AZURE_WEBAPP_NAME` para o nome do App Service que você criou no Passo 1.
    ```yaml
    env:
      AZURE_WEBAPP_NAME: app-central-atendimento-19055 # <-- Altere aqui!
      PYTHON_VERSION: '3.10'
    ```

### Passo 4: Configurar a Aplicação na Azure

O App Service precisa das mesmas variáveis de ambiente que você usa localmente.

1.  Vá para o seu **App Service** no Portal do Azure.
2.  No menu lateral, vá para **Configuration > Application settings**.
3.  Adicione as seguintes configurações:
    -   `DATABASE_URL`: A string de conexão do seu banco de dados PostgreSQL no Azure.
    -   `SECRET_KEY`: A mesma chave secreta forte que você usaria em produção.
4.  Ainda em **Configuration**, vá para a aba **General settings** e defina o **Startup Command**. Você tem duas opções:
    -   **Opção A (Direto):** Cole o comando no campo "Startup Command":
        ```
        gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app
        ```
    -   **Opção B (Via Script):** Use o script `startup.sh` incluído no projeto, que é ideal para lógicas de inicialização mais complexas no futuro. No campo "Startup Command", digite:
        ```
        ./startup.sh
        ```
5.  **Salve as alterações**. O App Service será reiniciado.

### Passo 5: Ativar o Pipeline

Faça o commit e o push das alterações que você fez no arquivo `deploy.yml`.

```bash
git add .github/workflows/deploy.yml
git commit -m "ci: Configurar nome do App Service no workflow"
git push origin master
```
Este push irá acionar o pipeline. Vá para a aba **"Actions"** no seu repositório GitHub para acompanhar o deploy. Após a conclusão, sua API estará funcional na URL do Azure.

---


## 🤔 Solução de Problemas (Troubleshooting)

<details>
<summary><strong>Erro local: `column ... does not exist`</strong></summary>

-   **Causa:** Seu banco de dados local está dessincronizado com os modelos da aplicação.
-   **Solução:** Pare a aplicação e execute o script de reset: `python reset_db.py`. **Atenção**: Isso apagará todos os dados locais.
</details>

<details>
<summary><strong>Erro no Azure CLI: `ResourceGroupNotFound`</strong></summary>

-   **Causa:** O grupo de recursos que você especificou em um comando não foi encontrado.
-   **Solução:** Verifique se o nome está correto ou crie o grupo de recursos primeiro com `az group create --name "seu-nome-de-grupo" --location "sua-localizacao"`.
</details>

<details>
<summary><strong>Erro no Azure CLI: `The subscription is not registered to use namespace 'Microsoft.Web'`</strong></summary>

-   **Causa:** Sua assinatura do Azure precisa habilitar o provedor de recursos para criar Aplicativos Web.
-   **Solução:** Execute o comando `az provider register --namespace Microsoft.Web` e aguarde alguns minutos antes de tentar novamente.
</details>

<details>
<summary><strong>Erro no CI/CD: `DATABASE_URL Field required` ou `SECRET_KEY Field required`</strong></summary>

-   **Causa:** O passo de `pytest` no pipeline do GitHub Actions precisa das variáveis de ambiente para inicializar a aplicação, mesmo que os testes usem um banco de dados em memória.
-   **Solução:** O arquivo `deploy.yml` já inclui variáveis de ambiente "dummy" para o passo de teste. Se o erro persistir, verifique se essa configuração foi removida acidentalmente.
</details>

---


## 🧪 Testes Automatizados

Para rodar a suíte de testes localmente e garantir a qualidade do código:
```bash
pytest
```
O pipeline de CI/CD também executa esses testes antes de cada deploy, prevenindo que bugs cheguem à produção.

---


## 📁 Estrutura do Projeto

A estrutura do código é organizada por responsabilidades para facilitar a manutenção.
```
central-atendimento-azure/
├── .github/
│   └── workflows/
│       └── deploy.yml         # Workflow de CI/CD para Azure
├── src/
│   ├── main.py                # Ponto de entrada da aplicação FastAPI
│   ├── config/                # Módulos de configuração (BD, .env)
│   ├── models/                # Modelos ORM do SQLAlchemy (tabelas)
│   ├── schemas/               # Schemas Pydantic (validação de dados da API)
│   ├── routes/                # Endpoints da API (rotas)
│   └── services/              # Lógica de negócio (ex: classificação com IA)
├── tests/                     # Testes automatizados
├── .env.example               # Arquivo de exemplo para variáveis de ambiente
├── requirements.txt           # Dependências travadas (gerado por pip-tools)
├── startup.sh                 # Script de inicialização para o App Service
└── reset_db.py                # Script para resetar o banco de dados de dev
```

---


## 📈 Roadmap

-   [x] **v1.1**: Autenticação JWT implementada.
-   [x] **v1.2**: Pipeline de CI/CD com GitHub Actions.
-   [ ] **v1.3**: Integração real com **Azure Cognitive Services**, WhatsApp Business API, SendGrid.
-   [ ] **v2.0**: Arquitetura multi-tenant, ML para priorização, integração com CRMs.

---


## 📝 Licença e Contato

Este projeto está sob a licença MIT.

Desenvolvido por **Julio Okuda**.
-   **LinkedIn:** [linkedin.com/in/juliookuda](https://www.linkedin.com/in/juliookuda/)
-   **GitHub:** [@Jcnok](https://github.com/Jcnok)

```

🗺️ Próximos Passos - Implementação de Agentes LLM
✅ Fase 1 Concluída
 Arquitetura de agentes projetada
 Infraestrutura Azure provisionada
 Router Agent implementado e testado
 Dependências instaladas
 Banco de dados configurado
🚀 Fase 2: Agentes Especializados (Próximas 2-3 semanas)
1. Financial Agent (Prioridade Alta)
Objetivo: Automatizar solicitações financeiras (boletos, pagamentos, faturas)

Tarefas:

 Criar src/agents/financial_agent.py
 Implementar tools:
generate_boleto(cliente_id, valor) → integrar com 
src/routes/boletos.py
check_payment_status(boleto_id) → consultar status
get_invoices(cliente_id, periodo) → listar faturas
 Definir system prompt com regras de validação
 Implementar fallback para humano
 Criar testes unitários
 Testar com casos reais
Estimativa: 3-4 dias

2. Technical Agent (Prioridade Alta)
Objetivo: Diagnosticar problemas técnicos e criar tickets

Tarefas:

 Criar src/agents/technical_agent.py
 Implementar tools:
search_knowledge_base(query) → buscar soluções conhecidas
create_ticket(description, priority) → criar chamado
check_system_status() → verificar status de serviços
 Implementar RAG (Retrieval-Augmented Generation):
Buscar conversas similares em conversation_memory
Usar embeddings para similarity search
 Definir processo de diagnóstico estruturado
 Criar testes unitários
 Popular knowledge base com problemas comuns
Estimativa: 4-5 dias

3. Sales Agent (Prioridade Média)
Objetivo: Auxiliar em upgrades, downgrades e vendas

Tarefas:

 Criar src/agents/sales_agent.py
 Implementar tools:
get_customer_profile(cliente_id) → perfil do cliente
get_plan_recommendations(usage_data) → sugerir planos
calculate_upgrade_cost(current_plan, new_plan) → calcular custo
 Definir abordagem consultiva (não agressiva)
 Integrar com CRM (se disponível)
 Criar testes unitários
Estimativa: 3 dias

4. General Agent (Prioridade Baixa)
Objetivo: Lidar com interações gerais e FAQ

Tarefas:

 Criar src/agents/general_agent.py
 Implementar tools:
search_faq(query) → buscar em FAQ
get_company_info(topic) → informações institucionais
 Popular FAQ com perguntas comuns
 Criar testes unitários
Estimativa: 2 dias

🔧 Fase 3: Integração e Orquestração (1 semana)
1. Agent Orchestrator
Objetivo: Coordenar múltiplos agentes em uma conversa

Tarefas:

 Criar src/agents/orchestrator.py
 Implementar lógica de roteamento dinâmico
 Gerenciar contexto entre agentes
 Implementar handoff entre agentes
 Adicionar logging e observabilidade
2. Memory Management
Objetivo: Implementar memória de curto e longo prazo

Tarefas:

 Criar src/memory/session_manager.py (Redis)
 Criar src/memory/conversation_store.py (PostgreSQL)
 Implementar embedding e storage de conversas
 Criar função de similarity search
 Implementar TTL e cleanup automático
3. API Integration
Objetivo: Expor agentes via API REST

Tarefas:

 Criar endpoint /api/agents/chat
 Implementar streaming de respostas (SSE)
 Adicionar rate limiting
 Implementar autenticação por cliente
 Documentar API no Swagger
📊 Fase 4: Monitoramento e Otimização (1 semana)
1. Observabilidade
Tarefas:

 Configurar Application Insights dashboards
 Implementar custom metrics:
Taxa de resolução por agente
Latência média
Custo por conversa
CSAT por agente
 Configurar alertas críticos
 Criar runbook de operação
2. Otimização de Custos
Tarefas:

 Implementar cache de respostas frequentes (Redis)
 Otimizar prompts (reduzir tokens)
 Implementar batch processing para embeddings
 Configurar rate limiting inteligente
3. Testes de Carga
Tarefas:

 Criar testes de carga com Locust/k6
 Simular 1000 req/min
 Identificar gargalos
 Otimizar performance
🎯 Fase 5: Produção (1 semana)
1. Rollout Gradual
Tarefas:

 Deploy em staging
 Testes com usuários beta (10%)
 Coletar feedback
 Ajustar prompts e comportamento
 Aumentar para 25%, 50%, 100%
2. Documentação Final
Tarefas:

 Atualizar README com guia completo
 Criar documentação de API
 Criar guia de troubleshooting
 Documentar runbook de operação
📅 Timeline Estimado
Fase	Duração	Prazo
Fase 2: Agentes Especializados	2-3 semanas	Semana 1-3
Fase 3: Integração	1 semana	Semana 4
Fase 4: Monitoramento	1 semana	Semana 5
Fase 5: Produção	1 semana	Semana 6
Total: ~6 semanas para MVP completo em produção

🎓 Próxima Ação Imediata
Começar com Financial Agent:

# 1. Criar arquivo do agente
touch src/agents/financial_agent.py
# 2. Implementar estrutura básica
# 3. Testar com casos simples
# 4. Integrar com Router Agent
Comando para iniciar:

# Exemplo de estrutura inicial
class FinancialAgent:
    def __init__(self):
        self.kernel = Kernel()
        # ... configuração
    
    async def handle(self, message: str, context: dict) -> dict:
        # Lógica do agente
        pass
💡 Dicas de Implementação
Comece simples: Implemente um agente por vez
Teste constantemente: Use pytest após cada feature
Monitore custos: Acompanhe gastos no Azure Portal
Itere nos prompts: Ajuste baseado em feedback real
Documente decisões: Mantenha um log de design decisions