import json
import re
from pathlib import Path
from .output_guard_result import OutputGuardResult
from . import severity as sev


class PatternDetector:
    def __init__(self, rules_path: str | None = None):
        self.patterns: list[dict] = []
        if rules_path:
            self.load_rules(rules_path)
        else:
            default_path = Path(__file__).parent / "rules" / "default_output_patterns.json"
            if default_path.exists():
                self.load_rules(str(default_path))

    def load_rules(self, path: str):
        with open(path, "r") as f:
            raw = json.load(f)
        for name, cfg in raw.items():
            self.patterns.append({
                "name": name,
                "pattern": cfg["pattern"],
                "type": cfg.get("type", "unknown"),
                "severity": cfg.get("severity", "FULL_LEAK"),
                "action": cfg.get("action", "REDACT"),
                "placeholder": cfg.get("placeholder", "[REDACTED_SECRET]"),
            })

    def add_pattern(self, name: str, pattern: str, severity: str = "FULL_LEAK",
                    action: str = "REDACT", placeholder: str = "[REDACTED_SECRET]"):
        self.patterns.append({
            "name": name,
            "pattern": pattern,
            "type": "custom",
            "severity": severity,
            "action": action,
            "placeholder": placeholder,
        })

    def detect(self, text: str) -> list[dict]:
        findings = []
        for cfg in self.patterns:
            matches = re.finditer(cfg["pattern"], text, re.DOTALL)
            for m in matches:
                findings.append({
                    "name": cfg["name"],
                    "type": cfg["type"],
                    "matched_text": m.group(),
                    "start": m.start(),
                    "end": m.end(),
                    "severity": cfg["severity"],
                    "action": cfg["action"],
                    "placeholder": cfg["placeholder"],
                })
        return findings
