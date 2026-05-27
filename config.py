import json
from pathlib import Path


class Config:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or str(
            Path(__file__).parent / "policies" / "defense_rules.json"
        )
        self._data = self._load()

    def _load(self) -> dict:
        path = Path(self.config_path)
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    @property
    def ollama_url(self) -> str:
        return self.get("ollama_url", "http://localhost:11434")

    @property
    def model(self) -> str:
        return self.get("model", "mistral")

    @property
    def threshold(self) -> str:
        return self.get("default_threshold", "medium")

    @property
    def max_buffer_size(self) -> int:
        return self.get("max_buffer_size", 1000)

    @property
    def rejection_message(self) -> str:
        return self.get("rejection_message", "[SecretGuard]\n此內容受到限制，未經授權無法提供。")

    @property
    def defense_layers(self) -> list[str]:
        return self.get("defense_layers", [
            "input_guard", "restricted_token_guard", "skill_layer",
            "risk_level_guard", "output_guard",
        ])

    def reload(self):
        self._data = self._load()
