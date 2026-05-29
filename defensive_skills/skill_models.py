from dataclasses import dataclass, field


ACTION_SEVERITY = {
    "ALLOW": 0,
    "WARN": 1,
    "REWRITE": 2,
    "RESTRICT": 3,
    "AUTHORIZE": 4,
    "ESCALATE": 5,
    "BLOCK": 6,
}


def highest_severity_action(actions: list[str]) -> str:
    return max(actions, key=lambda a: ACTION_SEVERITY.get(a, 0))


def merge_unique(*lists):
    seen = set()
    result = []
    for lst in lists:
        for item in lst:
            if item not in seen:
                seen.add(item)
                result.append(item)
    return result


@dataclass
class SkillInput:
    original_prompt: str
    normalized_prompt: str
    attack_category: str
    policy_action: str
    risk_score: int = 0
    protected_assets: list[dict] = field(default_factory=list)
    session_context: dict = field(default_factory=dict)
    user_role: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class DetectionResult:
    matched: bool
    confidence: float = 0.0
    matched_rules: list[str] = field(default_factory=list)
    matched_assets: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    risk_tags: list[str] = field(default_factory=list)


@dataclass
class DefenseResult:
    action: str
    safe_prompt: str | None = None
    response_message: str | None = None
    restrictions: list[str] = field(default_factory=list)
    risk_tags: list[str] = field(default_factory=list)
    runtime_checks: list[str] = field(default_factory=list)
    evidence: dict = field(default_factory=dict)
