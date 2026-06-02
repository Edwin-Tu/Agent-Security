from dataclasses import dataclass, field


@dataclass
class OutputGuardResult:
    original_output: str
    safe_output: str
    action: str
    is_blocked: bool
    is_redacted: bool
    leakage_detected: bool
    matched_patterns: list[str] = field(default_factory=list)
    matched_assets: list[str] = field(default_factory=list)
    risk_level: str = "none"
    reasons: list[str] = field(default_factory=list)
