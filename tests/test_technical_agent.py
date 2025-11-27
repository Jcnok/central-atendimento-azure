import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
from src.agents.technical_agent import TechnicalAgent, TechnicalPlugin
from src.services.technical_service import TechnicalService

# ================== PLUGIN TESTS ==================

def test_technical_plugin_search_kb():
    plugin = TechnicalPlugin()
    with patch.object(TechnicalService, 'search_knowledge_base') as mock_method:
        mock_method.return_value = [{"topic": "internet", "content": "Reinicie o modem"}]
        result = plugin.search_knowledge_base("internet lenta")
        assert "Reinicie o modem" in result
        mock_method.assert_called_with("internet lenta")

def test_technical_plugin_search_kb_empty():
    plugin = TechnicalPlugin()
    with patch.object(TechnicalService, 'search_knowledge_base') as mock_method:
        mock_method.return_value = []
        result = plugin.search_knowledge_base("assunto desconhecido")
        assert "Não encontrei informações" in result

def test_technical_plugin_create_ticket():
    plugin = TechnicalPlugin()
    with patch.object(TechnicalService, 'create_ticket') as mock_method:
        mock_method.return_value = {"ticket_id": "TKT-123"}
        result = plugin.create_ticket("Sem internet", "alta")
        assert "TKT-123" in result
        mock_method.assert_called_with("Sem internet", "alta")

def test_technical_plugin_check_status():
    plugin = TechnicalPlugin()
    with patch.object(TechnicalService, 'check_system_status') as mock_method:
        mock_method.return_value = {"internet": "ok"}
        result = plugin.check_system_status()
        assert '"internet": "ok"' in result

# ================== AGENT TESTS ==================

@pytest.fixture
def mock_kernel():
    with patch("src.agents.technical_agent.Kernel") as MockKernel:
        kernel_instance = MockKernel.return_value
        kernel_instance.add_service = MagicMock()
        kernel_instance.add_plugin = MagicMock()
        
        chat_service = AsyncMock()
        kernel_instance.get_service.return_value = chat_service
        
        chat_message = MagicMock()
        chat_message.__str__.return_value = "Reinicie o modem"
        chat_service.get_chat_message_content.return_value = chat_message
        
        yield kernel_instance

@pytest.fixture
def mock_azure_chat_completion():
    with patch("src.agents.technical_agent.AzureChatCompletion") as MockClass:
        yield MockClass

@pytest.mark.asyncio
async def test_technical_agent_initialization(mock_kernel, mock_azure_chat_completion):
    with patch("src.agents.technical_agent.settings") as mock_settings:
        mock_settings.AZURE_OPENAI_KEY = "dummy"
        mock_settings.AZURE_OPENAI_ENDPOINT = "dummy"
        
        agent = TechnicalAgent()
        assert agent.kernel is not None
        agent.kernel.add_service.assert_called_once()
        agent.kernel.add_plugin.assert_called_once()
        mock_azure_chat_completion.assert_called_once()

@pytest.mark.asyncio
async def test_process_message(mock_kernel, mock_azure_chat_completion):
    with patch("src.agents.technical_agent.settings") as mock_settings:
        mock_settings.AZURE_OPENAI_KEY = "dummy"
        mock_settings.AZURE_OPENAI_ENDPOINT = "dummy"
        
        agent = TechnicalAgent()
        response = await agent.process_message("Minha internet caiu")
        assert response == "Reinicie o modem"
        
        chat_service = agent.kernel.get_service.return_value
        chat_service.get_chat_message_content.assert_called_once()
