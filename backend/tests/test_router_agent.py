"""
Unit tests for Router Agent
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.router_agent import RouterAgent


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    with patch('src.agents.router_agent.settings') as mock:
        mock.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com"
        mock.AZURE_OPENAI_KEY = "test-key"
        mock.AZURE_OPENAI_DEPLOYMENT_GPT4O_MINI = "gpt-4o-mini"
        mock.AZURE_OPENAI_API_VERSION = "2024-08-01-preview"
        yield mock


@pytest.fixture
def mock_kernel():
    """Mock Semantic Kernel"""
    with patch('src.agents.router_agent.Kernel') as MockKernel:
        kernel_instance = MockKernel.return_value
        yield kernel_instance


@pytest.fixture
def router_agent(mock_settings, mock_kernel):
    """Create Router Agent instance for testing"""
    with patch('src.agents.router_agent.AzureChatCompletion'):
        return RouterAgent()


@pytest.mark.asyncio
async def test_route_financial_intent(router_agent, mock_kernel):
    """Test routing of financial-related message"""
    # Mock LLM response
    mock_response = MagicMock()
    mock_response.__str__ = lambda self: '{"agent": "financial_agent", "confidence": 0.95, "reasoning": "Solicitação de boleto"}'
    
    # Setup mock service
    mock_chat_service = AsyncMock()
    mock_chat_service.get_chat_message_content = AsyncMock(return_value=mock_response)
    mock_kernel.get_service.return_value = mock_chat_service
        
    result = await router_agent.route("Preciso da segunda via do meu boleto")
    
    assert result["agent"] == "financial_agent"
    assert result["confidence"] > 0.9
    assert "boleto" in result["reasoning"].lower()


@pytest.mark.asyncio
async def test_route_technical_intent(router_agent, mock_kernel):
    """Test routing of technical support message"""
    mock_response = MagicMock()
    mock_response.__str__ = lambda self: '{"agent": "technical_agent", "confidence": 0.92, "reasoning": "Problema técnico"}'
    
    mock_chat_service = AsyncMock()
    mock_chat_service.get_chat_message_content = AsyncMock(return_value=mock_response)
    mock_kernel.get_service.return_value = mock_chat_service
        
    result = await router_agent.route("Meu sistema está com erro")
    
    assert result["agent"] == "technical_agent"
    assert result["confidence"] > 0.9


@pytest.mark.asyncio
async def test_route_with_context(router_agent, mock_kernel):
    """Test routing with additional context"""
    mock_response = MagicMock()
    mock_response.__str__ = lambda self: '{"agent": "sales_agent", "confidence": 0.88, "reasoning": "Interesse em upgrade"}'
    
    mock_chat_service = AsyncMock()
    mock_chat_service.get_chat_message_content = AsyncMock(return_value=mock_response)
    mock_kernel.get_service.return_value = mock_chat_service
        
    context = {"cliente_id": 123, "current_plan": "basic"}
    result = await router_agent.route("Quero fazer upgrade", context=context)
    
    assert result["agent"] == "sales_agent"
    assert "confidence" in result


@pytest.mark.asyncio
async def test_route_invalid_agent_fallback(router_agent, mock_kernel):
    """Test fallback to general_agent when invalid agent is returned"""
    mock_response = MagicMock()
    mock_response.__str__ = lambda self: '{"agent": "invalid_agent", "confidence": 0.5, "reasoning": "Test"}'
    
    mock_chat_service = AsyncMock()
    mock_chat_service.get_chat_message_content = AsyncMock(return_value=mock_response)
    mock_kernel.get_service.return_value = mock_chat_service
        
    result = await router_agent.route("Test message")
    
    assert result["agent"] == "general_agent"
    assert result["confidence"] == 0.5


@pytest.mark.asyncio
async def test_route_json_parse_error(router_agent, mock_kernel):
    """Test handling of invalid JSON response"""
    mock_response = MagicMock()
    mock_response.__str__ = lambda self: 'Invalid JSON'
    
    mock_chat_service = AsyncMock()
    mock_chat_service.get_chat_message_content = AsyncMock(return_value=mock_response)
    mock_kernel.get_service.return_value = mock_chat_service
        
    result = await router_agent.route("Test message")
    
    assert result["agent"] == "general_agent"
    assert result["confidence"] == 0.0
    assert "Erro" in result["reasoning"]


def test_list_agents(router_agent):
    """Test listing available agents"""
    agents = router_agent.list_agents()
    
    assert "financial_agent" in agents
    assert "technical_agent" in agents
    assert "sales_agent" in agents
    assert "general_agent" in agents
    assert len(agents) == 4


@pytest.mark.asyncio
async def test_get_agent_info(router_agent):
    """Test getting agent information"""
    info = await router_agent.get_agent_info("financial_agent")
    
    assert info is not None
    assert "Boletos" in info or "pagamentos" in info
