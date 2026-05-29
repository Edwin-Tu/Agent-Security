from defensive_skills.base_skill import BaseSkill
from .routing_context import RoutingContext


RISK_TO_ACTION = {
    "critical": "BLOCK",
    "high": "BLOCK",
    "medium": "RESTRICT",
    "low": "WARN",
}


class SkillAdapter:
    def __init__(self, skill: BaseSkill):
        self._skill = skill
        self.name = skill.name
        self.category = skill.name

    def detect(self, context: RoutingContext) -> dict:
        prompt = context.prompt
        session = context.session_context or {}
        threat_info = self._skill.detect(prompt, session)
        detected = threat_info.get("detected", False)
        risk = threat_info.get("risk", "low")
        action = RISK_TO_ACTION.get(risk, "WARN")
        return {
            "skill": self.name,
            "detected": detected,
            "action": action,
            "reason": f"Detected by {self.name}: {threat_info.get('pattern', 'unknown')}",
            "risk": risk,
            "pattern": threat_info.get("pattern"),
        }

    def defend(self, context: RoutingContext) -> dict:
        prompt = context.prompt
        session = context.session_context or {}
        threat_info = self._skill.detect(prompt, session)
        sanitized = self._skill.defend(prompt, threat_info)
        risk = threat_info.get("risk", "low")
        action = RISK_TO_ACTION.get(risk, "WARN")
        return {
            "skill": self.name,
            "detected": True,
            "action": action,
            "reason": f"Defended by {self.name}",
            "sanitized": sanitized,
            "rewritten_prompt": sanitized if action == "REWRITE" else None,
        }

    def __getattr__(self, name):
        return getattr(self._skill, name)
