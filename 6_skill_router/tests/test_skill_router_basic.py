import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from skill_router.routing_context import RoutingContext
from skill_router.routing_result import RoutingResult
from skill_router.skill_registry import SkillRegistry
from skill_router.skill_router import SkillRouter


class MockDetectSkill:
    name: str = "MockDetectSkill"
    category: str = "mock_category"

    def detect(self, context: RoutingContext) -> dict:
        return {
            "skill": self.name,
            "detected": True,
            "action": "RESTRICT",
            "reason": "Mock detection triggered",
        }

    def defend(self, context: RoutingContext) -> dict:
        return {
            "skill": self.name,
            "detected": True,
            "action": "RESTRICT",
            "reason": "Mock defense applied",
            "constraints": ["Mock constraint"],
        }


def make_router():
    registry = SkillRegistry()
    registry.register("mock_category", MockDetectSkill())
    router = SkillRouter(registry=registry)
    return router


class TestBasicRouting:
    def test_single_category_finds_correct_skill(self):
        router = make_router()
        context = RoutingContext(
            prompt="test prompt",
            attack_categories=["mock_category"],
            policy_action="RESTRICT",
            risk_score=50,
        )
        result = router.route(context)
        assert "MockDetectSkill" in result.selected_skills

    def test_route_returns_routing_result(self):
        router = make_router()
        context = RoutingContext(
            prompt="test prompt",
            attack_categories=["mock_category"],
            policy_action="RESTRICT",
            risk_score=50,
        )
        result = router.route(context)
        assert isinstance(result, RoutingResult)

    def test_selected_skills_content_correct(self):
        router = make_router()
        context = RoutingContext(
            prompt="test prompt",
            attack_categories=["mock_category"],
            policy_action="RESTRICT",
            risk_score=50,
        )
        result = router.route(context)
        assert "MockDetectSkill" in result.selected_skills
        assert len(result.selected_skills) == 1

    def test_executed_skills_content_correct(self):
        router = make_router()
        context = RoutingContext(
            prompt="test prompt",
            attack_categories=["mock_category"],
            policy_action="RESTRICT",
            risk_score=50,
        )
        result = router.route(context)
        assert "MockDetectSkill" in result.executed_skills
        assert len(result.skill_results) > 0
