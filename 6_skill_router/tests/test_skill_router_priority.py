import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from skill_router.routing_context import RoutingContext
from skill_router.skill_registry import SkillRegistry
from skill_router.skill_router import SkillRouter


class HighPrioritySkill:
    name: str = "HighPrioritySkill"
    category: str = "critical"

    def detect(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "BLOCK", "reason": "Critical"}

    def defend(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "BLOCK", "reason": "Blocked"}


class LowPrioritySkill:
    name: str = "LowPrioritySkill"
    category: str = "low_risk"

    def detect(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "WARN", "reason": "Low risk"}

    def defend(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "WARN", "reason": "Logged"}


class MediumPrioritySkill:
    name: str = "MediumPrioritySkill"
    category: str = "medium_risk"

    def detect(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "RESTRICT", "reason": "Medium risk"}

    def defend(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "RESTRICT", "reason": "Restricted"}


def make_router():
    registry = SkillRegistry()
    registry.register("critical", HighPrioritySkill(), priority=100)
    registry.register("medium_risk", MediumPrioritySkill(), priority=50)
    registry.register("low_risk", LowPrioritySkill(), priority=10)
    router = SkillRouter(registry=registry)
    return router


class TestPriority:
    def test_high_risk_skill_comes_first(self):
        router = make_router()
        context = RoutingContext(
            prompt="test",
            attack_categories=["critical", "medium_risk", "low_risk"],
            policy_action="BLOCK",
            risk_score=90,
        )
        result = router.route(context)
        assert result.selected_skills[0] == "HighPrioritySkill"

    def test_priority_order_is_stable(self):
        router = make_router()
        context = RoutingContext(
            prompt="test",
            attack_categories=["low_risk", "medium_risk", "critical"],
            policy_action="BLOCK",
            risk_score=90,
        )
        result1 = router.route(context)
        result2 = router.route(context)
        assert result1.selected_skills == result2.selected_skills

    def test_block_type_prioritized_over_warn(self):
        registry = SkillRegistry()
        registry.register("critical", HighPrioritySkill(), priority=100)
        registry.register("low_risk", LowPrioritySkill(), priority=10)
        router = SkillRouter(registry=registry)
        context = RoutingContext(
            prompt="test",
            attack_categories=["low_risk", "critical"],
            policy_action="BLOCK",
            risk_score=95,
        )
        result = router.route(context)
        assert result.selected_skills.index("HighPrioritySkill") < result.selected_skills.index("LowPrioritySkill")
