from api.openai_adapter import messages_to_prompt
from entry.secretguard_pipeline import SecretGuardPipeline
from llm_gateway.ollama_provider import OllamaProvider
from llm_gateway.base_provider import ProviderError


class OllamaAdapter:
    def __init__(self):
        self.pipeline = SecretGuardPipeline()

    def list_tags(self) -> dict:
        provider = OllamaProvider()
        try:
            models_data = provider.list_models()
        except ProviderError:
            models_data = []
        models = [
            {"name": m["name"], "model": m["name"]}
            for m in models_data
        ]
        return {"models": models}

    def generate(self, model: str, prompt: str, stream: bool = False) -> dict:
        req = type("Req", (), {
            "model": model,
            "prompt": prompt,
            "session_id": "default",
            "role": "user",
            "stream": False,
            "options": {},
        })()

        provider = OllamaProvider()
        result = self.pipeline.chat(req, provider)
        content = result.response or (result.error_message or "")

        return {
            "model": model,
            "response": content,
            "done": True,
        }

    def chat(self, model: str, messages: list[dict], stream: bool = False) -> dict:
        prompt = messages_to_prompt(messages)

        req = type("Req", (), {
            "model": model,
            "prompt": prompt,
            "session_id": "default",
            "role": "user",
            "stream": False,
            "options": {},
        })()

        provider = OllamaProvider()
        result = self.pipeline.chat(req, provider)
        content = result.response or (result.error_message or "")

        return {
            "model": model,
            "message": {"role": "assistant", "content": content},
            "done": True,
        }
