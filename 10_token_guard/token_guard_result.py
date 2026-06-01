from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class TokenMatch:
    asset_id: str
    matched_text: str
    match_type: str  # exact / partial / alias / encoded / normalized
    risk_level: str
    start: int | None = None
    end: int | None = None
    reason: str | None = None


@dataclass
class TokenGuardResult:
    allowed: bool
    action: str      # ALLOW / WARN / RESTRICT / BLOCK / ESCALATE / REWRITE_REQUIRED
    risk_level: str  # low / medium / high / critical
    matches: list[TokenMatch]
    restricted_tokens: list[RestrictedToken]
    sanitized_prompt: str | None = None
    reasons: list[str] = field(default_factory=list)
