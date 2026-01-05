from fastapi import HTTPException, Security, Request, Depends
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_429_TOO_MANY_REQUESTS
from langgraph.memory.redis_store import RedisStore
import os
import time

# API Key Auth
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# In production, fetch valid keys from DB or Vault
VALID_API_KEYS = {
    "test-client": "secret-key-123",
    "siem-prod": "prod-key-456"
}

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header in VALID_API_KEYS.values():
        return api_key_header
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )

# Rate Limiting
# Simple fixed window counter
redis_store = RedisStore(host="localhost", port=6379) # Should use env vars

async def rate_limiter(request: Request, api_key: str = Depends(get_api_key)):
    # Limit: 100 requests per minute per key
    limit = 100
    window = 60
    
    key = f"rate_limit:{api_key}"
    current = redis_store.client.incr(key)
    
    if current == 1:
        redis_store.client.expire(key, window)
        
    if current > limit:
        raise HTTPException(
            status_code=HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded"
        )
    return True
