from abc import ABC, abstractmethod
from typing import Dict, Any

class ModelAdapter(ABC):
    @abstractmethod
    def predict(self, prompt: str, max_tokens: int = 200, temp: float = 0.7) -> Dict[str, Any]:
        """
        Generates text and returns metadata.
        Returns:
            {
                "text": str,
                "prompt_tokens": int,
                "completion_tokens": int,
                "model_version": str
            }
        """
        pass
