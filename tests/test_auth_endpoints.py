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
            json={"username": "testuser2", "password": "password"},
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
