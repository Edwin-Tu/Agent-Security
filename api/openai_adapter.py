from entry.secretguard_pipeline import SecretGuardPipeline


def messages_to_prompt(messages: list[dict]) -> str:
    parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        parts.append(f"[{role}]\n{content}")
    return "\n\n".join(parts)


class OpenAIAdapter:
    def __init__(self):
        self.pipeline = SecretGuardPipeline()

    def chat_completion(self, model: str, messages: list[dict], stream: bool = False):
        prompt = messages_to_prompt(messages)

        req = type("Req", (), {
            "model": model,
            "prompt": prompt,
            "session_id": "default",
            "role": "user",
            "stream": False,
            "options": {},
        })()

        from llm_gateway.ollama_provider import OllamaProvider
        provider = OllamaProvider()
        result = self.pipeline.chat(req, provider)

        event_id = result.event_id or "unknown"
        content = result.response or (result.error_message or "")

        return {
            "id": f"chatcmpl_{event_id}",
            "object": "chat.completion",
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
            "secretguard": {
                "allowed": result.allowed,
                "action": result.action,
                "risk_score": result.risk_score,
                "attack_type": result.attack_type or "unknown",
                "event_id": event_id,
            },
        }
