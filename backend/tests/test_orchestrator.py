import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.agents.orchestrator import AgentOrchestrator

@pytest.fixture
def mock_router():
    with patch("src.agents.orchestrator.RouterAgent") as MockRouter:
        router_instance = MockRouter.return_value
        router_instance.route = AsyncMock()
        yield router_instance

@pytest.fixture
def mock_agents():
    with patch("src.agents.orchestrator.FinancialAgent") as MockFin, \
         patch("src.agents.orchestrator.TechnicalAgent") as MockTech, \
         patch("src.agents.orchestrator.SalesAgent") as MockSales, \
         patch("src.agents.orchestrator.GeneralAgent") as MockGen:
        
        fin = MockFin.return_value
        tech = MockTech.return_value
        sales = MockSales.return_value
        gen = MockGen.return_value
        
        fin.process_message = AsyncMock(return_value="Financial Response")
        tech.process_message = AsyncMock(return_value="Technical Response")
        sales.process_message = AsyncMock(return_value="Sales Response")
        gen.process_message = AsyncMock(return_value="General Response")
        
        yield {
            "financial_agent": fin,
            "technical_agent": tech,
            "sales_agent": sales,
            "general_agent": gen
        }

@pytest.mark.asyncio
async def test_orchestrator_routing_financial(mock_router, mock_agents):
    mock_router.route.return_value = {"agent": "financial_agent", "confidence": 0.9}
    
    orchestrator = AgentOrchestrator()
    # We need to manually inject the mocks because __init__ is called before we can patch the instance attributes
    # But since we patched the classes, the __init__ already used the mocks.
    # Let's verify.
    
    result = await orchestrator.process_message("Boleto")
    
    assert result["agent_used"] == "financial_agent"
    assert result["response"] == "Financial Response"
    mock_agents["financial_agent"].process_message.assert_called_once()

@pytest.mark.asyncio
async def test_orchestrator_fallback(mock_router, mock_agents):
    # Test unknown agent
    mock_router.route.return_value = {"agent": "unknown_agent", "confidence": 0.5}
    
    orchestrator = AgentOrchestrator()
    result = await orchestrator.process_message("Ola")
    
    assert result["agent_used"] == "general_agent"
    assert result["response"] == "General Response"

@pytest.mark.asyncio
async def test_orchestrator_error(mock_router, mock_agents):
    mock_router.route.side_effect = Exception("Router Error")
    
    orchestrator = AgentOrchestrator()
    result = await orchestrator.process_message("Crash")
    
    assert result["agent_used"] == "system_error"
    assert "erro interno" in result["response"]
