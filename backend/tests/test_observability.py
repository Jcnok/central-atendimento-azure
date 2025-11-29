import pytest
from unittest.mock import MagicMock, patch
from fastapi import FastAPI
from src.config.observability import setup_observability

def test_setup_observability_no_connection_string():
    app = FastAPI()
    with patch("src.config.observability.settings") as mock_settings:
        mock_settings.APPLICATIONINSIGHTS_CONNECTION_STRING = None
        
        # Should log info and return without error
        setup_observability(app)

def test_setup_observability_with_connection_string():
    app = FastAPI()
    with patch("src.config.observability.settings") as mock_settings:
        mock_settings.APPLICATIONINSIGHTS_CONNECTION_STRING = "InstrumentationKey=fake"
        
        # Mock the modules that are imported inside the function
        mock_azure_monitor = MagicMock()
        mock_opentelemetry = MagicMock()
        
        with patch.dict('sys.modules', {
            'azure.monitor.opentelemetry': mock_azure_monitor,
            'opentelemetry.instrumentation.fastapi': mock_opentelemetry
        }):
            setup_observability(app)
            
            mock_azure_monitor.configure_azure_monitor.assert_called_once()
            mock_opentelemetry.FastAPIInstrumentor.instrument_app.assert_called_once_with(app)

def test_setup_observability_import_error():
    app = FastAPI()
    with patch("src.config.observability.settings") as mock_settings:
        mock_settings.APPLICATIONINSIGHTS_CONNECTION_STRING = "InstrumentationKey=fake"
        
        # Simulate import error
        with patch.dict('sys.modules', {'azure.monitor.opentelemetry': None}):
            setup_observability(app)
            # Should catch ImportError and log warning, not crash
