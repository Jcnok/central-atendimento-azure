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
