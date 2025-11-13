"""
Testes básicos dos endpoints da API
Execute com: pytest tests/ -v
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.config.database import SessionLocal, Base, engine

# Criar cliente de teste
client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Setup do banco de dados para testes"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

class TestHealthCheck:
    """Testes de health check"""
    
    def test_health_check_root(self):
        """Testa GET /"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_health_check_health(self):
        """Testa GET /health"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

class TestClientes:
    """Testes de clientes"""
    
    def test_criar_cliente(self):
        """Testa criação de cliente"""
        response = client.post(
            "/clientes/",
            json={
                "nome": "João Silva",
                "email": "joao@example.com",
                "telefone": "11999999999",
                "canal_preferido": "whatsapp"
            }
        )
        assert response.status_code == 201
        assert response.json()["id"] == 1
    
    def test_obter_cliente(self):
        """Testa obtenção de cliente"""
        # Criar cliente primeiro
        client.post(
            "/clientes/",
            json={
                "nome": "Maria Silva",
                "email": "maria@example.com",
                "telefone": "11988888888"
            }
        )
        
        # Obter cliente
        response = client.get("/clientes/1")
        assert response.status_code == 200
        assert response.json()["nome"] == "João Silva"
    
    def test_listar_clientes(self):
        """Testa listagem de clientes"""
        response = client.get("/clientes/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_criar_cliente_email_duplicado(self):
        """Testa erro ao criar cliente com email duplicado"""
        response = client.post(
            "/clientes/",
            json={
                "nome": "João Duplicado",
                "email": "joao@example.com",  # Email já existe
                "telefone": "11977777777"
            }
        )
        assert response.status_code == 400

class TestChamados:
    """Testes de chamados"""
    
    @pytest.fixture(autouse=True)
    def setup_cliente(self):
        """Setup de cliente para testes"""
        response = client.post(
            "/clientes/",
            json={
                "nome": "Cliente Teste",
                "email": f"teste{id(self)}@example.com",
                "telefone": "11999999999"
            }
        )
        self.cliente_id = response.json()["id"]
    
    def test_criar_chamado_com_resolucao_automatica(self):
        """Testa criação de chamado que é resolvido automaticamente"""
        response = client.post(
            "/chamados/",
            json={
                "cliente_id": 1,
                "canal": "site",
                "mensagem": "segunda via boleto"
            }
        )
        assert response.status_code == 201
        assert response.json()["resolvido_automaticamente"] == True
        assert "segunda via" in response.json()["resposta"].lower()
    
    def test_criar_chamado_para_encaminhamento(self):
        """Testa criação de chamado que é encaminhado para humano"""
        response = client.post(
            "/chamados/",
            json={
                "cliente_id": 1,
                "canal": "whatsapp",
                "mensagem": "meu sistema está com erro grave"
            }
        )
        assert response.status_code == 201
        assert response.json()["resolvido_automaticamente"] == False
        assert response.json()["encaminhado_para_humano"] == True
    
    def test_obter_chamado(self):
        """Testa obtenção de chamado"""
        # Criar chamado
        create_response = client.post(
            "/chamados/",
            json={
                "cliente_id": 1,
                "canal": "email",
                "mensagem": "qual meu plano?"
            }
        )
        chamado_id = create_response.json()["chamado_id"]
        
        # Obter chamado
        response = client.get(f"/chamados/{chamado_id}")
        assert response.status_code == 200
    
    def test_listar_chamados(self):
        """Testa listagem de chamados"""
        response = client.get("/chamados/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_listar_chamados_por_canal(self):
        """Testa filtro por canal"""
        response = client.get("/chamados/?canal=site")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

class TestMetricas:
    """Testes de métricas"""
    
    def test_obter_metricas_gerais(self):
        """Testa obtenção de métricas gerais"""
        response = client.get("/metricas/")
        assert response.status_code == 200
        assert "total_chamados" in response.json()
        assert "taxa_resolucao_automatica" in response.json()
    
    def test_metricas_por_canal(self):
        """Testa métricas por canal"""
        response = client.get("/metricas/por-canal")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
    
    def test_metricas_por_status(self):
        """Testa métricas por status"""
        response = client.get("/metricas/por-status")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
