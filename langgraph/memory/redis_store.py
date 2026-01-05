import redis
import json
from typing import Optional, Dict, Any
import os

class RedisStore:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.ttl = 3600  # 1 hour default TTL

    def set_context(self, session_id: str, data: Dict[str, Any], ttl: Optional[int] = None):
        """
        Stores context with a TTL.
        """
        self.client.setex(
            f"session:{session_id}",
            ttl or self.ttl,
            json.dumps(data)
        )

    def get_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves context.
        """
        data = self.client.get(f"session:{session_id}")
        if data:
            return json.loads(data)
        return None

    def clear_context(self, session_id: str):
        self.client.delete(f"session:{session_id}")
