import json
from datetime import datetime, timezone


class SessionMemory:
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.history: list[dict] = []
        self.interactions: int = 0
        self.blocked_count: int = 0
        self.alerts: list[dict] = []
        self.session_id: str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    def record(self, interaction: dict):
        interaction["timestamp"] = datetime.now(timezone.utc).isoformat()
        interaction["session_id"] = self.session_id
        self.history.append(interaction)
        self.interactions += 1
        if interaction.get("blocked", False):
            self.blocked_count += 1
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def add_alert(self, alert_type: str, message: str, detail: dict = None):
        self.alerts.append({
            "type": alert_type,
            "message": message,
            "detail": detail or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def recent(self, n: int = 5) -> list[dict]:
        return self.history[-n:]

    def stats(self) -> dict:
        return {
            "session_id": self.session_id,
            "total_interactions": self.interactions,
            "blocked_count": self.blocked_count,
            "block_rate": round(self.blocked_count / max(self.interactions, 1), 3),
            "alert_count": len(self.alerts),
        }

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "max_history": self.max_history,
            "history": self.history,
            "interactions": self.interactions,
            "blocked_count": self.blocked_count,
            "alerts": self.alerts,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def reset(self):
        self.history.clear()
        self.interactions = 0
        self.blocked_count = 0
        self.alerts.clear()
