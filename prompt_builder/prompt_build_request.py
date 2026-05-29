from dataclasses import dataclass, field


@dataclass
class PromptBuildRequest:
    original_prompt: str
    normalized_prompt: str | None = None
    policy_action: str = "ALLOW"
    risk_score: int = 0
    attack_categories: list[str] = field(default_factory=list)
    protected_assets: list[dict] = field(default_factory=list)
    enabled_skills: list[str] = field(default_factory=list)
    allowed_scope: list[str] = field(default_factory=list)
    denied_scope: list[str] = field(default_factory=list)
    role: str = "guest"
    session_risk_level: str = "low"
    defense_notes: list[str] = field(default_factory=list)
