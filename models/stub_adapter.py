from models.adapter import ModelAdapter
from typing import Dict, Any
from middleware.accounting import TokenAccountant
from infra.db import SessionLocal

class StubAdapter(ModelAdapter):
    def __init__(self):
        self.accountant = TokenAccountant(SessionLocal())

    def predict(self, prompt: str, max_tokens: int = 200, temp: float = 0.7) -> Dict[str, Any]:
        # Deterministic stub
        result = {
            "text": "This is a stubbed response for testing.",
            "prompt_tokens": 10,
            "completion_tokens": 8,
            "model_version": "stub-v1"
        }
        
        self.accountant.check_and_log("stub_agent", result)
        return result
