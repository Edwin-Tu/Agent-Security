from dataclasses import dataclass, field


@dataclass
class RoutingResult:
    selected_skills: list[str]
    executed_skills: list[str]
    skill_results: list[dict]
    recommended_action: str
    rewritten_prompt: str | None = None
    added_constraints: list[str] | None = None
    runtime_monitor_level: str = "normal"
    blocked: bool = False
    reasons: list[str] | None = None
