from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ProtectedAsset:
    asset_id: str
    name: str
    type: str
    value: str | None = None
    aliases: list[str] = field(default_factory=list)
    risk_level: str = "high"
    protection_modes: list[str] = field(default_factory=list)


@dataclass
class RestrictedToken:
    asset_id: str
    token: str
    token_type: str  # exact / partial / alias / encoded / normalized
    risk_level: str
    source: str      # asset_value / alias / generated_variant / policy
