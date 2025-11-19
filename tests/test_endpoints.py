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
