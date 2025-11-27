import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
from src.agents.sales_agent import SalesAgent, SalesPlugin
from src.services.sales_service import SalesService

# ================== PLUGIN TESTS ==================

def test_sales_plugin_get_profile():
    plugin = SalesPlugin()
    with patch.object(SalesService, 'get_customer_profile') as mock_method:
        mock_method.return_value = {"plan": "basic"}
        result = plugin.get_customer_profile(1)
        assert '"plan": "basic"' in result
        mock_method.assert_called_with(1)

def test_sales_plugin_recommendations():
    plugin = SalesPlugin()
    with patch.object(SalesService, 'get_plan_recommendations') as mock_method:
        mock_method.return_value = [{"plan": "premium"}]
        result = plugin.get_plan_recommendations(1)
        assert "premium" in result

def test_sales_plugin_recommendations_empty():
    plugin = SalesPlugin()
    with patch.object(SalesService, 'get_plan_recommendations') as mock_method:
        mock_method.return_value = []
        result = plugin.get_plan_recommendations(1)
        assert "adequado" in result

def test_sales_plugin_calc_cost():
    plugin = SalesPlugin()
    with patch.object(SalesService, 'calculate_upgrade_cost') as mock_method:
        mock_method.return_value = "R$ 50,00"
        result = plugin.calculate_upgrade_cost("A", "B")
        assert "R$ 50,00" in result

# ================== AGENT TESTS ==================

@pytest.fixture
def mock_kernel():
    with patch("src.agents.sales_agent.Kernel") as MockKernel:
        kernel_instance = MockKernel.return_value
        kernel_instance.add_service = MagicMock()
        kernel_instance.add_plugin = MagicMock()
        
        chat_service = AsyncMock()
        kernel_instance.get_service.return_value = chat_service
        
        chat_message = MagicMock()
        chat_message.__str__.return_value = "Recomendo o plano Fibra 600"
        chat_service.get_chat_message_content.return_value = chat_message
        
        yield kernel_instance

@pytest.fixture
def mock_azure_chat_completion():
    with patch("src.agents.sales_agent.AzureChatCompletion") as MockClass:
        yield MockClass

@pytest.mark.asyncio
async def test_sales_agent_initialization(mock_kernel, mock_azure_chat_completion):
    with patch("src.agents.sales_agent.settings") as mock_settings:
        mock_settings.AZURE_OPENAI_KEY = "dummy"
        mock_settings.AZURE_OPENAI_ENDPOINT = "dummy"
        
        agent = SalesAgent()
        assert agent.kernel is not None
        agent.kernel.add_service.assert_called_once()
        agent.kernel.add_plugin.assert_called_once()
        mock_azure_chat_completion.assert_called_once()

@pytest.mark.asyncio
async def test_process_message(mock_kernel, mock_azure_chat_completion):
    with patch("src.agents.sales_agent.settings") as mock_settings:
        mock_settings.AZURE_OPENAI_KEY = "dummy"
        mock_settings.AZURE_OPENAI_ENDPOINT = "dummy"
        
        agent = SalesAgent()
        response = await agent.process_message("Quero melhorar minha internet")
        assert response == "Recomendo o plano Fibra 600"
        
        chat_service = agent.kernel.get_service.return_value
        chat_service.get_chat_message_content.assert_called_once()
