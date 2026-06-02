import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from skill_router.routing_context import RoutingContext
from skill_router.skill_registry import SkillRegistry
from skill_router.skill_router import SkillRouter


class MockSkillA:
    name: str = "MockSkillA"
    category: str = "category_a"

    def detect(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "RESTRICT", "reason": "A detected"}

    def defend(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "RESTRICT", "reason": "A defended",
                "constraints": ["A constraint"]}


class MockSkillB:
    name: str = "MockSkillB"
    category: str = "category_b"

    def detect(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "RESTRICT", "reason": "B detected"}

    def defend(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "RESTRICT", "reason": "B defended",
                "constraints": ["B constraint"]}


def make_router():
    registry = SkillRegistry()
    registry.register("category_a", MockSkillA())
    registry.register("category_b", MockSkillB())
    router = SkillRouter(registry=registry)
    return router


class TestMultiCategory:
    def test_multi_category_loads_multiple_skills(self):
        router = make_router()
        context = RoutingContext(
            prompt="multi attack",
            attack_categories=["category_a", "category_b"],
            policy_action="RESTRICT",
            risk_score=70,
        )
        result = router.route(context)
        assert "MockSkillA" in result.selected_skills
        assert "MockSkillB" in result.selected_skills

    def test_duplicate_skill_appears_only_once(self):
        registry = SkillRegistry()
        registry.register("category_a", MockSkillA())
        registry.register("category_b", MockSkillA())
        router = SkillRouter(registry=registry)
        context = RoutingContext(
            prompt="test",
            attack_categories=["category_a", "category_b"],
            policy_action="RESTRICT",
            risk_score=50,
        )
        result = router.route(context)
        assert result.selected_skills.count("MockSkillA") == 1

    def test_multi_skill_results_merged(self):
        router = make_router()
        context = RoutingContext(
            prompt="multi attack",
            attack_categories=["category_a", "category_b"],
            policy_action="RESTRICT",
            risk_score=70,
        )
        result = router.route(context)
        assert len(result.skill_results) >= 2
        skills_in_results = [r["skill"] for r in result.skill_results]
        assert "MockSkillA" in skills_in_results
        assert "MockSkillB" in skills_in_results
