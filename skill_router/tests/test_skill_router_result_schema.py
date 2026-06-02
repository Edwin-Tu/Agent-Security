import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from skill_router.routing_result import RoutingResult
from skill_router.routing_context import RoutingContext
from skill_router.skill_registry import SkillRegistry
from skill_router.skill_router import SkillRouter


class MockSkill:
    name: str = "MockSchemaSkill"
    category: str = "schema_test"

    def detect(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "RESTRICT", "reason": "test"}

    def defend(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "RESTRICT", "reason": "defended",
                "constraints": ["test constraint"]}


class TestResultSchema:
    def test_result_contains_selected_skills(self):
        result = RoutingResult(
            selected_skills=["SkillA"],
            executed_skills=[],
            skill_results=[],
            recommended_action="ALLOW",
            blocked=False,
        )
        assert hasattr(result, "selected_skills")
        assert isinstance(result.selected_skills, list)

    def test_result_contains_executed_skills(self):
        result = RoutingResult(
            selected_skills=[],
            executed_skills=["SkillA"],
            skill_results=[],
            recommended_action="ALLOW",
            blocked=False,
        )
        assert hasattr(result, "executed_skills")
        assert isinstance(result.executed_skills, list)

    def test_result_contains_skill_results(self):
        result = RoutingResult(
            selected_skills=[],
            executed_skills=[],
            skill_results=[{"skill": "SkillA", "detected": True}],
            recommended_action="ALLOW",
            blocked=False,
        )
        assert hasattr(result, "skill_results")
        assert isinstance(result.skill_results, list)

    def test_result_contains_recommended_action(self):
        result = RoutingResult(
            selected_skills=[],
            executed_skills=[],
            skill_results=[],
            recommended_action="RESTRICT",
            blocked=False,
        )
        assert result.recommended_action == "RESTRICT"

    def test_result_contains_blocked(self):
        result = RoutingResult(
            selected_skills=[],
            executed_skills=[],
            skill_results=[],
            recommended_action="ALLOW",
            blocked=True,
        )
        assert result.blocked is True

    def test_empty_input_returns_stable_format(self):
        router = SkillRouter(registry=SkillRegistry())
        context = RoutingContext(
            prompt="",
            attack_categories=[],
            policy_action="ALLOW",
            risk_score=0,
        )
        result = router.route(context)
        assert isinstance(result.selected_skills, list)
        assert isinstance(result.executed_skills, list)
        assert isinstance(result.skill_results, list)
        assert isinstance(result.recommended_action, str)
        assert isinstance(result.blocked, bool)
