import json
from pathlib import Path
from datetime import datetime, timezone


class ReportGenerator:
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or str(Path(__file__).parent)

    def generate_from_log(self, log_path: str) -> dict:
        path = Path(log_path)
        if not path.exists():
            return {"error": "Log file not found."}
        events = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return self._build_report(events)

    def _build_report(self, events: list[dict]) -> dict:
        total = len(events)
        blocked = sum(1 for e in events if e.get("blocked", False))
        actions = {}
        for e in events:
            a = e.get("policy_action", "unknown")
            actions[a] = actions.get(a, 0) + 1
        return {
            "report_time": datetime.now(timezone.utc).isoformat(),
            "total_events": total,
            "blocked_events": blocked,
            "block_rate": round(blocked / max(total, 1), 3),
            "action_distribution": actions,
            "events": events,
        }

    def save_report(self, report: dict, filename: str = None) -> str:
        if filename is None:
            filename = f"report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        path = Path(self.output_dir) / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return str(path)
