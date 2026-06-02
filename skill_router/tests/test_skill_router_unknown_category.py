import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from skill_router.routing_context import RoutingContext
from skill_router.routing_result import RoutingResult
from skill_router.skill_registry import SkillRegistry
from skill_router.skill_router import SkillRouter


def make_router():
    registry = SkillRegistry()
    router = SkillRouter(registry=registry)
    return router


class TestUnknownCategory:
    def test_unknown_category_does_not_crash(self):
        router = make_router()
        context = RoutingContext(
            prompt="unknown attack",
            attack_categories=["nonexistent_category"],
            policy_action="WARN",
            risk_score=30,
        )
        result = router.route(context)
        assert isinstance(result, RoutingResult)

    def test_routing_result_still_produced(self):
        router = make_router()
        context = RoutingContext(
            prompt="unknown attack",
            attack_categories=["unknown_1", "unknown_2"],
            policy_action="WARN",
            risk_score=30,
        )
        result = router.route(context)
        assert result is not None
        assert isinstance(result, RoutingResult)

    def test_reasons_record_unknown_category(self):
        router = make_router()
        context = RoutingContext(
            prompt="unknown attack",
            attack_categories=["unknown_category_xyz"],
            policy_action="WARN",
            risk_score=30,
        )
        result = router.route(context)
        assert result.reasons is not None
        assert any("unknown" in r.lower() for r in result.reasons)

    def test_selected_skills_empty_for_unknown(self):
        router = make_router()
        context = RoutingContext(
            prompt="unknown attack",
            attack_categories=["unknown_category_xyz"],
            policy_action="WARN",
            risk_score=30,
        )
        result = router.route(context)
        assert result.selected_skills == []
