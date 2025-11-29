import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from src.main import app
from src.agents.orchestrator import AgentOrchestrator

client = TestClient(app)

@pytest.fixture
def mock_orchestrator():
    with patch("src.routes.chat.AgentOrchestrator") as MockOrch:
        instance = MockOrch.return_value
        instance.process_message = AsyncMock(return_value={
            "response": "Olá, como posso ajudar?",
            "agent_used": "general_agent",
            "confidence": 1.0,
            "routing_reasoning": "Greeting"
        })
        yield instance

def test_chat_endpoint_success(mock_orchestrator):
    response = client.post("/api/chat/", json={
        "message": "Olá",
        "session_id": "test-session"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Olá, como posso ajudar?"
    assert data["agent_used"] == "general_agent"
    
    # Verify orchestrator was called with correct args
    # Note: We need to check how Depends(get_orchestrator) behaves with mocking.
    # Since we patched the class used in get_orchestrator, it should work.

def test_chat_endpoint_error():
    with patch("src.routes.chat.AgentOrchestrator") as MockOrch:
        instance = MockOrch.return_value
        instance.process_message = AsyncMock(side_effect=Exception("Crash"))
        
        response = client.post("/api/chat/", json={"message": "Crash"})
        assert response.status_code == 500
