from models.local_adapter import LocalAdapter
from typing import Optional

class LocalLLM:
    def __init__(self, model_name: str = "orca-mini-3b-gguf2-q4_0.gguf", model_path: Optional[str] = None):
        # We now wrap the Adapter instead of raw GPT4All
        self.adapter = LocalAdapter(model_name, model_path)

    def generate(self, prompt: str, max_tokens: int = 200, temp: float = 0.7) -> str:
        """
        Generates text from the model.
        """
        # Adapter returns dict with metadata, we just want text here for backward compatibility
        result = self.adapter.predict(prompt, max_tokens=max_tokens, temp=temp)
        return result["text"]

    def generate_with_system_prompt(self, system_prompt: str, user_prompt: str, max_tokens: int = 200) -> str:
        """
        Generates text using a system prompt and user prompt.
        """
        # Construct prompt manually to pass to adapter
        full_prompt = f"System: {system_prompt}\nUser: {user_prompt}\nAssistant:"
        result = self.adapter.predict(full_prompt, max_tokens=max_tokens)
        return result["text"]
