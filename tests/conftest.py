import uuid
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.config.database import Base, get_db
from src.main import app

# ================== CONFIGURAÇÃO DO BANCO DE DADOS DE TESTE ==================

# Usar arquivo para permitir compartilhamento entre sync (testes) e async (app)
TEST_DB_FILE = "./test.db"
SQLALCHEMY_DATABASE_URL_SYNC = f"sqlite:///{TEST_DB_FILE}"
SQLALCHEMY_DATABASE_URL_ASYNC = f"sqlite+aiosqlite:///{TEST_DB_FILE}"

# Engine Síncrona (para os testes verificarem o banco)
engine_sync = create_engine(
    SQLALCHEMY_DATABASE_URL_SYNC,
    connect_args={"check_same_thread": False},
    poolclass=NullPool,
)

# Habilitar WAL mode
from sqlalchemy import text
with engine_sync.connect() as conn:
    conn.execute(text("PRAGMA journal_mode=WAL"))

TestingSessionSync = sessionmaker(autocommit=False, autoflush=False, bind=engine_sync)

# Engine Assíncrona (para a aplicação rodar)
engine_async = create_async_engine(
    SQLALCHEMY_DATABASE_URL_ASYNC,
    connect_args={"check_same_thread": False},
    poolclass=NullPool,
)
TestingSessionAsync = async_sessionmaker(
    bind=engine_async,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# ================== SOBRESCRITA DA DEPENDÊNCIA DO BANCO ==================


async def override_get_db():
    async with TestingSessionAsync() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


# ================== FIXTURE DE SETUP DO BANCO ==================


@pytest.fixture(scope="function")
def db_session():
    # Remove arquivo anterior se existir
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
        
    # Cria tabelas usando engine síncrona
    Base.metadata.create_all(bind=engine_sync)
    
    db = TestingSessionSync()
    yield db
    db.close()
    
    # Limpeza
    # Base.metadata.drop_all(bind=engine_sync)
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Client fixture that depends on db_session to ensure a fresh DB for each test.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def auth_token(client): # Client agora é fixture
    """
    Fixture that creates a user, logs in, and returns an auth token.
    """
    unique_username = f"testuser_{uuid.uuid4().hex}"
    unique_email = f"test_{uuid.uuid4().hex}@example.com"

    signup_response = client.post(
        "/api/auth/signup",
        json={
            "username": unique_username,
            "email": unique_email,
            "password": "password",
        },
    )
    assert signup_response.status_code == 200, f"Signup failed: {signup_response.text}"

    login_response = client.post(
        "/api/auth/login",
        data={"username": unique_username, "password": "password"},
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"

    token = login_response.json().get("access_token")
    assert token is not None
    return token
