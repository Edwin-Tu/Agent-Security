"""Report generation helpers for SecretGuard."""

from __future__ import annotations

import json
from pathlib import Path


class ReportGenerator:
    """Generate JSON and Markdown reports from guardrail results."""

    def __init__(self, output_dir: str | Path | None = None):
        self.output_dir = Path(output_dir) if output_dir else Path("reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def to_json(self, payload: dict) -> str:
        return json.dumps(payload, ensure_ascii=False, indent=2)

    def to_markdown(self, payload: dict) -> str:
        lines = ["# SecretGuard Report", "", f"- Total events: {payload.get('total_events', 0)}", f"- Blocked: {payload.get('blocked', 0)}"]
        for item in payload.get("items", []):
            lines.extend([
                "",
                f"## {item.get('label', 'Item')}",
                f"- Risk: {item.get('level', 'unknown')}",
                f"- Action: {item.get('action', 'unknown')}",
            ])
        return "\n".join(lines) + "\n"

    def write_json(self, payload: dict, filename: str = "report.json") -> Path:
        path = self.output_dir / filename
        path.write_text(self.to_json(payload), encoding="utf-8")
        return path

    def write_markdown(self, payload: dict, filename: str = "report.md") -> Path:
        path = self.output_dir / filename
        path.write_text(self.to_markdown(payload), encoding="utf-8")
        return path
