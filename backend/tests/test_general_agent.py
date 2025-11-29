import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
from src.agents.general_agent import GeneralAgent, GeneralPlugin
from src.services.general_service import GeneralService

# ================== PLUGIN TESTS ==================

def test_general_plugin_search_faq():
    plugin = GeneralPlugin()
    with patch.object(GeneralService, 'search_faq') as mock_method:
        mock_method.return_value = [{"topic": "horario", "content": "24h"}]
        result = plugin.search_faq("horario")
        assert "24h" in result
        mock_method.assert_called_with("horario")

def test_general_plugin_info():
    plugin = GeneralPlugin()
    with patch.object(GeneralService, 'get_company_info') as mock_method:
        mock_method.return_value = "Av Paulista"
        result = plugin.get_company_info("endereco")
        assert "Av Paulista" in result

# ================== AGENT TESTS ==================

@pytest.fixture
def mock_kernel():
    with patch("src.agents.general_agent.Kernel") as MockKernel:
        kernel_instance = MockKernel.return_value
        kernel_instance.add_service = MagicMock()
        kernel_instance.add_plugin = MagicMock()
        
        chat_service = AsyncMock()
        kernel_instance.get_service.return_value = chat_service
        
        chat_message = MagicMock()
        chat_message.__str__.return_value = "Nosso horario é 24h"
        chat_service.get_chat_message_content.return_value = chat_message
        
        yield kernel_instance

@pytest.fixture
def mock_azure_chat_completion():
    with patch("src.agents.general_agent.AzureChatCompletion") as MockClass:
        yield MockClass

@pytest.mark.asyncio
async def test_general_agent_initialization(mock_kernel, mock_azure_chat_completion):
    with patch("src.agents.general_agent.settings") as mock_settings:
        mock_settings.AZURE_OPENAI_KEY = "dummy"
        mock_settings.AZURE_OPENAI_ENDPOINT = "dummy"
        
        agent = GeneralAgent()
        assert agent.kernel is not None
        agent.kernel.add_service.assert_called_once()
        agent.kernel.add_plugin.assert_called_once()
        mock_azure_chat_completion.assert_called_once()

@pytest.mark.asyncio
async def test_process_message(mock_kernel, mock_azure_chat_completion):
    with patch("src.agents.general_agent.settings") as mock_settings:
        mock_settings.AZURE_OPENAI_KEY = "dummy"
        mock_settings.AZURE_OPENAI_ENDPOINT = "dummy"
        
        agent = GeneralAgent()
        response = await agent.process_message("Qual o horario?")
        assert response == "Nosso horario é 24h"
        
        chat_service = agent.kernel.get_service.return_value
        chat_service.get_chat_message_content.assert_called_once()
