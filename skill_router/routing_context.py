from dataclasses import dataclass, field


@dataclass
class RoutingContext:
    prompt: str
    attack_categories: list[str]
    policy_action: str
    risk_score: int
    protected_assets: list[dict] | None = None
    matched_rules: list[dict] | None = None
    session_context: dict | None = None
    user_role: str | None = None

    VALID_POLICY_ACTIONS = {"ALLOW", "WARN", "REWRITE", "RESTRICT", "BLOCK", "AUTHORIZE", "ESCALATE"}

    def __post_init__(self):
        if self.policy_action not in self.VALID_POLICY_ACTIONS:
            raise ValueError(f"Invalid policy_action: {self.policy_action}. Must be one of {self.VALID_POLICY_ACTIONS}")
