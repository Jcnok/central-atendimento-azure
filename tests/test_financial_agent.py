import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
from src.agents.financial_agent import FinancialAgent, FinancialPlugin
from src.services.financial_service import FinancialService

# ================== PLUGIN TESTS ==================

def test_financial_plugin_generate_boleto():
    plugin = FinancialPlugin()
    with patch.object(FinancialService, 'gerar_boleto_simulado') as mock_method:
        mock_method.return_value = {"codigo": "123"}
        result = plugin.generate_boleto("test@example.com")
        assert "123" in result
        mock_method.assert_called_with("test@example.com", None)

def test_financial_plugin_generate_boleto_error():
    plugin = FinancialPlugin()
    with patch.object(FinancialService, 'gerar_boleto_simulado') as mock_method:
        mock_method.return_value = None
        result = plugin.generate_boleto("erro@example.com")
        assert "Não foi possível" in result

def test_financial_plugin_check_payment_status():
    plugin = FinancialPlugin()
    with patch.object(FinancialService, 'check_payment_status') as mock_method:
        mock_method.return_value = "pago"
        result = plugin.check_payment_status("123")
        assert "pago" in result

def test_financial_plugin_get_invoices():
    plugin = FinancialPlugin()
    with patch.object(FinancialService, 'get_invoices') as mock_method:
        mock_method.return_value = [{"id": 1}]
        result = plugin.get_invoices(1)
        assert '[{"id": 1}]' in result

# ================== AGENT TESTS ==================

@pytest.fixture
def mock_kernel():
    with patch("src.agents.financial_agent.Kernel") as MockKernel:
        kernel_instance = MockKernel.return_value
        # Mock add_service and add_plugin
        kernel_instance.add_service = MagicMock()
        kernel_instance.add_plugin = MagicMock()
        
        # Mock get_service
        chat_service = AsyncMock()
        kernel_instance.get_service.return_value = chat_service
        
        # Mock get_chat_message_content response
        chat_message = MagicMock()
        chat_message.__str__.return_value = "Resposta do agente"
        chat_service.get_chat_message_content.return_value = chat_message
        
        yield kernel_instance

@pytest.fixture
def mock_azure_chat_completion():
    with patch("src.agents.financial_agent.AzureChatCompletion") as MockClass:
        yield MockClass

@pytest.mark.asyncio
async def test_financial_agent_initialization(mock_kernel, mock_azure_chat_completion):
    # Mock settings to ensure keys are present
    with patch("src.agents.financial_agent.settings") as mock_settings:
        mock_settings.AZURE_OPENAI_KEY = "dummy"
        mock_settings.AZURE_OPENAI_ENDPOINT = "dummy"
        
        agent = FinancialAgent()
        assert agent.kernel is not None
        agent.kernel.add_service.assert_called_once()
        agent.kernel.add_plugin.assert_called_once()
        mock_azure_chat_completion.assert_called_once()

@pytest.mark.asyncio
async def test_process_message(mock_kernel, mock_azure_chat_completion):
    with patch("src.agents.financial_agent.settings") as mock_settings:
        mock_settings.AZURE_OPENAI_KEY = "dummy"
        mock_settings.AZURE_OPENAI_ENDPOINT = "dummy"
        
        agent = FinancialAgent()
        response = await agent.process_message("Quero meu boleto")
        assert response == "Resposta do agente"
        
        # Verify get_chat_message_content was called
        chat_service = agent.kernel.get_service.return_value
        chat_service.get_chat_message_content.assert_called_once()
