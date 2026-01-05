import pytest
from langgraph.memory.redis_store import RedisStore
from langgraph.memory.vector_store import VectorStore
from langgraph.memory.governance import MemoryGovernance
import time
import shutil
import os

# Fixtures
@pytest.fixture
def redis_store():
    # Mock or use real redis if available. 
    # For CI/local without docker running, we might need a mock.
    # But we set up docker-compose, so we assume it's running?
    # The user instructions said "Set up Docker Compose", but didn't say "Run it".
    # I should have run `docker-compose up -d` in initialization.
    # If I can't run docker, I should mock.
    # Given the environment, I'll try to use a mock for Redis to be safe and fast.
    
    class MockRedis:
        def __init__(self):
            self.data = {}
        def setex(self, key, ttl, value):
            self.data[key] = value
        def get(self, key):
            return self.data.get(key)
        def delete(self, key):
            if key in self.data:
                del self.data[key]

    store = RedisStore()
    store.client = MockRedis()
    return store

@pytest.fixture
def vector_store():
    # Use ephemeral client
    store = VectorStore(persist_directory=None)
    store.reset()
    return store

def test_redis_store(redis_store):
    redis_store.set_context("session-1", {"key": "value"})
    data = redis_store.get_context("session-1")
    assert data == {"key": "value"}
    
    redis_store.clear_context("session-1")
    assert redis_store.get_context("session-1") is None

def test_vector_store_allowlist(vector_store):
    # Allowed source
    vector_store.add_document("doc-1", "content", {"source": "playbook-ssh"})
    
    # Disallowed source
    with pytest.raises(ValueError, match="Source malicious-source is not in the allowlist"):
        vector_store.add_document("doc-2", "content", {"source": "malicious-source"})

def test_governance_flow(vector_store):
    gov = MemoryGovernance(vector_store)
    
    # Propose
    pid = gov.propose_memory_addition("New Rule", {"source": "policy-access-control"})
    assert gov.pending_writes[pid]["status"] == "PENDING"
    
    # Verify not in store yet
    results = vector_store.query("New Rule")
    assert len(results) == 0
    
    # Approve
    gov.approve_memory_addition(pid, "admin")
    assert gov.pending_writes[pid]["status"] == "APPROVED"
    
    # Verify in store
    results = vector_store.query("New Rule")
    assert len(results) > 0
    assert results[0]["content"] == "New Rule"

def test_governance_rejection(vector_store):
    gov = MemoryGovernance(vector_store)
    pid = gov.propose_memory_addition("Bad Rule", {"source": "policy-access-control"})
    
    gov.reject_memory_addition(pid, "admin")
    assert gov.pending_writes[pid]["status"] == "REJECTED"
    
    results = vector_store.query("Bad Rule")
    assert len(results) == 0
