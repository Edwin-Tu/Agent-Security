"""Config loading helpers for SecretGuard."""

from __future__ import annotations

from pathlib import Path

from .utils import load_json_file


class ConfigLoader:
    """Load and expose guardrail policies and thresholds from JSON files."""

    def __init__(self, policy_path: str | Path | None = None, thresholds_path: str | Path | None = None):
        self.policy_path = Path(policy_path) if policy_path else None
        self.thresholds_path = Path(thresholds_path) if thresholds_path else None

        self.policy = self._load_policy()
        self.thresholds = self._load_thresholds()

    def _load_policy(self) -> dict:
        if self.policy_path is None:
            return {
                "allow_low": True,
                "review_medium": True,
                "block_high": True,
                "block_critical": True,
                "redact_leakage": True,
                "max_prompt_length": 4000,
            }

        return load_json_file(self.policy_path)

    def _load_thresholds(self) -> dict:
        if self.thresholds_path is None:
            return {
                "review": 0.31,
                "block": 0.61,
                "critical": 0.81,
            }

        return load_json_file(self.thresholds_path)

    def get_threshold(self, name: str, default: float) -> float:
        return float(self.thresholds.get(name, default))
