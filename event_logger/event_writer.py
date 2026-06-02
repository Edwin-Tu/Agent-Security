import json
from pathlib import Path


class EventWriter:
    def __init__(self, log_path: str):
        self.log_path = log_path
        Path(self.log_path).parent.mkdir(parents=True, exist_ok=True)

    def write(self, event: dict) -> None:
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
