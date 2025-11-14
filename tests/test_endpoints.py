"""
Testes automatizados dos endpoints da API FastAPI.
Estes testes rodam em um banco de dados SQLite em memória para garantir
isolamento, segurança e velocidade.
"""

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
    connect_args={"check_same_thread": False},  # Necessário para SQLite
    poolclass=StaticPool,  # Recomendado para banco em memória
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ================== SOBRESCRITA DA DEPENDÊNCIA DO BANCO ==================


def override_get_db():
    """
    Dependência de banco de dados para ser usada durante os testes.
    Fornece uma sessão do banco de dados em memória.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Aplica a sobrescrita na aplicação FastAPI
app.dependency_overrides[get_db] = override_get_db


# ================== FIXTURE DE SETUP DO BANCO ==================


@pytest.fixture(scope="function")
def db_session():
    """
    Fixture que cria as tabelas antes de cada teste e as derruba depois.
    Garante que cada teste rode em um estado limpo.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


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
    def test_criar_cliente(self, db_session):
        email_unico = f"joao_{uuid.uuid4().hex}@example.com"
        response = client.post(
            "/clientes/",
            json={
                "nome": "João Silva",
                "email": email_unico,
                "telefone": "11999999999",
                "canal_preferido": "whatsapp",
            },
        )
        assert response.status_code == 201
        assert isinstance(response.json()["id"], int)

    def test_obter_cliente(self, db_session):
        email_unico = f"maria_{uuid.uuid4().hex}@example.com"
        response_create = client.post(
            "/clientes/",
            json={
                "nome": "Maria Silva",
                "email": email_unico,
                "telefone": "11988888888",
            },
        )
        cliente_id = response_create.json()["id"]
        response = client.get(f"/clientes/{cliente_id}")
        assert response.status_code == 200
        assert response.json()["nome"] == "Maria Silva"

    def test_listar_clientes(self, db_session):
        response = client.get("/clientes/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_criar_cliente_email_duplicado(self, db_session):
        email_unico = f"duplicado_{uuid.uuid4().hex}@example.com"
        client.post(
            "/clientes/",
            json={
                "nome": "Cliente Duplicado",
                "email": email_unico,
                "telefone": "11977777777",
            },
        )
        response = client.post(
            "/clientes/",
            json={
                "nome": "Cliente Duplicado 2",
                "email": email_unico,
                "telefone": "11977777778",
            },
        )
        assert response.status_code == 400


class TestChamados:
    def criar_cliente(self):
        email_unico = f"clientechamado_{uuid.uuid4().hex}@example.com"
        response = client.post(
            "/clientes/",
            json={
                "nome": "Cliente Chamados",
                "email": email_unico,
                "telefone": "11999999999",
            },
        )
        return response.json()["id"]

    def test_criar_chamado_com_resolucao_automatica(self, db_session):
        cliente_id = self.criar_cliente()
        response = client.post(
            "/chamados/",
            json={
                "cliente_id": cliente_id,
                "canal": "site",
                "mensagem": "segunda via boleto",
            },
        )
        assert response.status_code == 201
        assert response.json()["resolvido_automaticamente"] is True
        assert "segunda via" in response.json()["resposta"].lower()

    def test_criar_chamado_para_encaminhamento(self, db_session):
        cliente_id = self.criar_cliente()
        response = client.post(
            "/chamados/",
            json={
                "cliente_id": cliente_id,
                "canal": "whatsapp",
                "mensagem": "meu sistema está com erro grave",
            },
        )
        assert response.status_code == 201
        assert response.json()["resolvido_automaticamente"] is False
        assert response.json()["encaminhado_para_humano"] is True

    def test_obter_chamado(self, db_session):
        cliente_id = self.criar_cliente()
        create_response = client.post(
            "/chamados/",
            json={
                "cliente_id": cliente_id,
                "canal": "email",
                "mensagem": "qual meu plano?",
            },
        )
        chamado_id = create_response.json()["chamado_id"]
        response = client.get(f"/chamados/{chamado_id}")
        assert response.status_code == 200

    def test_listar_chamados(self, db_session):
        response = client.get("/chamados/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_listar_chamados_por_canal(self, db_session):
        response = client.get("/chamados/?canal=site")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestMetricas:
    def test_obter_metricas_gerais(self, db_session):
        response = client.get("/metricas/")
        assert response.status_code == 200
        assert "total_chamados" in response.json()
        assert "taxa_resolucao_automatica" in response.json()

    def test_metricas_por_canal(self, db_session):
        response = client.get("/metricas/por-canal")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_metricas_por_status(self, db_session):
        response = client.get("/metricas/por-status")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
