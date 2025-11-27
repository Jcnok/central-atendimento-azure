import json
import logging
from typing import Dict, Optional
import uuid
from datetime import timedelta

try:
    import redis
except ImportError:
    redis = None

from src.config.settings import settings

logger = logging.getLogger(__name__)

class SessionManager:
    """
    Manages short-term user sessions using Redis.
    Falls back to in-memory dictionary if Redis is not configured.
    """

    def __init__(self):
        self.redis_client = None
        self._local_cache = {}
        
        if settings.REDIS_HOST and redis:
            try:
                self.redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    password=settings.REDIS_PASSWORD,
                    ssl=settings.REDIS_SSL,
                    db=settings.REDIS_DB,
                    decode_responses=True
                )
                self.redis_client.ping()
                logger.info("✅ Connected to Redis for Session Management")
            except Exception as e:
                logger.warning(f"⚠️ Could not connect to Redis: {e}. Using in-memory fallback.")
                self.redis_client = None
        else:
            logger.info("ℹ️ Redis not configured. Using in-memory fallback for sessions.")

    def save_session(self, session_id: str, data: Dict, ttl_minutes: int = 30):
        """Save session data."""
        if self.redis_client:
            try:
                self.redis_client.setex(
                    f"session:{session_id}",
                    timedelta(minutes=ttl_minutes),
                    json.dumps(data)
                )
            except Exception as e:
                logger.error(f"Error saving session to Redis: {e}")
        else:
            self._local_cache[session_id] = data

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieve session data."""
        if self.redis_client:
            try:
                data = self.redis_client.get(f"session:{session_id}")
                return json.loads(data) if data else None
            except Exception as e:
                logger.error(f"Error getting session from Redis: {e}")
                return None
        else:
            return self._local_cache.get(session_id)

    def clear_session(self, session_id: str):
        """Delete session."""
        if self.redis_client:
            try:
                self.redis_client.delete(f"session:{session_id}")
            except Exception as e:
                logger.error(f"Error clearing session in Redis: {e}")
        else:
            if session_id in self._local_cache:
                del self._local_cache[session_id]
