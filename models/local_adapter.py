from models.adapter import ModelAdapter
from gpt4all import GPT4All
from typing import Dict, Any, Optional
from middleware.accounting import TokenAccountant
from infra.db import SessionLocal

class LocalAdapter(ModelAdapter):
    def __init__(self, model_name: str = "orca-mini-3b-gguf2-q4_0.gguf", model_path: Optional[str] = None):
        self.model = GPT4All(model_name, model_path=model_path, allow_download=False)
        self.model_name = model_name
        # In production, pass DB session properly. Here we create one.
        self.accountant = TokenAccountant(SessionLocal())

    def predict(self, prompt: str, max_tokens: int = 200, temp: float = 0.7) -> Dict[str, Any]:
        output = self.model.generate(prompt, max_tokens=max_tokens, temp=temp)
        
        # Estimate tokens (GPT4All might not give exact counts easily without encoding)
        # For MVP, we estimate: 1 token ~= 4 chars
        prompt_tokens = len(prompt) // 4
        completion_tokens = len(output) // 4
        
        result = {
            "text": output,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "model_version": self.model_name
        }
        
        # Log and Check Budget
        # This will raise exception if budget exceeded
        self.accountant.check_and_log("local_agent", result)
        
        return result
