from dataclasses import dataclass
from typing import Any, List, Union

from .policy_action import PolicyAction


@dataclass
class PolicyDecision:
    action: Union[PolicyAction, str]
    reason: str
    risk_score: int
    risk_level: str
    monitoring_level: str
    required_skills: List[str]
    prompt_constraints: List[str]
    should_block: bool
    should_rewrite: bool
    should_restrict: bool
    should_escalate: bool
    log_level: str

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def get(self, item: str, default: Any = None) -> Any:
        return getattr(self, item, default)
