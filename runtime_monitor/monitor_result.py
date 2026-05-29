from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class RuntimeMonitorResult:
    allowed: bool
    interrupted: bool
    reason: str
    matched_type: Optional[str] = None
    matched_value: Optional[str] = None
    risk_level: str = "low"
    safe_replacement: Optional[str] = None
