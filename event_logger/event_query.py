import json
from pathlib import Path


class EventQuery:
    def __init__(self, log_path: str):
        self.log_path = log_path

    def _read_all(self) -> list[dict]:
        path = Path(self.log_path)
        if not path.exists():
            return []
        events = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return events

    def all(self) -> list[dict]:
        return self._read_all()

    def latest(self, n: int) -> list[dict]:
        events = self._read_all()
        return events[-n:]

    def filter(self, **criteria) -> list[dict]:
        events = self._read_all()
        result = []
        for event in events:
            match = True
            for key, value in criteria.items():
                if key not in event:
                    match = False
                    break
                if event[key] != value:
                    match = False
                    break
            if match:
                result.append(event)
        return result
