import json
from pathlib import Path
from datetime import datetime, timezone


class EventLogger:
    def __init__(self, log_path: str = None):
        self.log_path = log_path or str(
            Path(__file__).resolve().parent.parent / "logs" / "guard_events.jsonl"
        )
        Path(self.log_path).parent.mkdir(parents=True, exist_ok=True)

    def log(self, event: dict):
        event["timestamp"] = datetime.now(timezone.utc).isoformat()
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def log_attack_event(self, attack_type: str, risk_score: int, policy_action: str,
                         blocked: bool, skills_used: list[str], leaked: bool = False):
        self.log({
            "type": "attack",
            "attack_type": attack_type,
            "risk_score": risk_score,
            "policy_action": policy_action,
            "blocked": blocked,
            "skills_used": skills_used,
            "leaked": leaked,
        })

    def read_events(self, limit: int = None) -> list[dict]:
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
        return events[:limit] if limit else events

    def get_attack_timeline(self) -> list[dict]:
        events = self.read_events()
        timeline = []
        for e in events:
            if e.get("type") == "attack":
                timeline.append({
                    "timestamp": e.get("timestamp", ""),
                    "attack_type": e.get("attack_type", ""),
                    "blocked": e.get("blocked", False),
                    "risk_score": e.get("risk_score", 0),
                })
        return sorted(timeline, key=lambda x: x.get("timestamp", ""))

    def get_statistics(self) -> dict:
        events = self.read_events()
        total = len(events)
        attack_events = [e for e in events if e.get("type") == "attack"]
        blocked = sum(1 for e in attack_events if e.get("blocked", False))
        leaked = sum(1 for e in attack_events if e.get("leaked", False))
        action_dist = {}
        for e in attack_events:
            a = e.get("policy_action", "unknown")
            action_dist[a] = action_dist.get(a, 0) + 1
        return {
            "total_events": total,
            "attack_events": len(attack_events),
            "blocked": blocked,
            "block_rate": round(blocked / max(len(attack_events), 1), 3),
            "leaked": leaked,
            "action_distribution": action_dist,
        }

    def clear(self):
        path = Path(self.log_path)
        if path.exists():
            path.unlink()
