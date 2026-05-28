from __future__ import annotations

from typing import Any


class SessionRiskTracker:
    def __init__(self, session_signals: list[str], rules: dict[str, Any]):
        self.session_signals = session_signals or []
        self.rules = rules

    def calculate_score(self) -> int:
        session_scores = self.rules.get("session_signal_scores", {})
        return sum(
            session_scores.get(signal, 0) for signal in self.session_signals
        )

    def high_risk_signals(self) -> list[str]:
        session_scores = self.rules.get("session_signal_scores", {})
        return [
            signal
            for signal in self.session_signals
            if session_scores.get(signal, 0) >= 25
        ]
