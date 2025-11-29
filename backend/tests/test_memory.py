import pytest
from unittest.mock import MagicMock, patch
from src.memory.session_manager import SessionManager
from src.memory.conversation_store import ConversationStore

# ================== SESSION MANAGER TESTS ==================

def test_session_manager_in_memory():
    # Force no redis
    with patch("src.memory.session_manager.redis", None):
        manager = SessionManager()
        manager.save_session("sess1", {"foo": "bar"})
        
        result = manager.get_session("sess1")
        assert result == {"foo": "bar"}
        
        manager.clear_session("sess1")
        assert manager.get_session("sess1") is None

def test_session_manager_redis_mock():
    # Mock redis
    mock_redis = MagicMock()
    mock_redis.get.return_value = '{"foo": "bar"}'
    
    with patch("src.memory.session_manager.redis") as MockRedisLib:
        MockRedisLib.Redis.return_value = mock_redis
        with patch("src.memory.session_manager.settings") as mock_settings:
            mock_settings.REDIS_HOST = "localhost"
            
            manager = SessionManager()
            result = manager.get_session("sess1")
            
            assert result == {"foo": "bar"}
            mock_redis.get.assert_called_with("session:sess1")

# ================== CONVERSATION STORE TESTS ==================

def test_conversation_store_add():
    mock_db = MagicMock()
    store = ConversationStore(mock_db)
    
    store.add_message(1, "user", "hello", "router")
    # Since it's a placeholder that logs, we just ensure it doesn't crash
    assert True
