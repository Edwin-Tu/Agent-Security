import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from skill_router.routing_context import RoutingContext
from skill_router.routing_result import RoutingResult
from skill_router.skill_registry import SkillRegistry
from skill_router.skill_router import SkillRouter
from skill_router.routing_rules_loader import RoutingRulesLoader


class MockSkill:
    def __init__(self, name: str):
        self.name = name
        self.category = name

    def detect(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "RESTRICT", "reason": f"{self.name} detected"}

    def defend(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "RESTRICT", "reason": f"{self.name} defended",
                "constraints": [f"{self.name} constraint"]}


ALL_CATEGORIES = [
    "direct_request", "encoding_bypass", "system_prompt_extraction",
    "multi_turn_probe", "instruction_override", "role_play",
    "partial_disclosure", "translation_bypass", "refusal_suppression",
    "output_constraint_bypass", "policy_confusion", "data_reconstruction",
    "format_smuggling",
]


def make_registry_with_all_skills():
    registry = SkillRegistry()
    for cat in ALL_CATEGORIES:
        registry.register(cat, MockSkill(cat))
    return registry


class TestRulesIntegration:
    def test_loads_routing_rules_file(self):
        loader = RoutingRulesLoader()
        rules = loader.load()
        assert isinstance(rules, dict)
        assert len(rules) > 0

    def test_all_categories_have_rules(self):
        loader = RoutingRulesLoader()
        rules = loader.load()
        for cat in ALL_CATEGORIES:
            assert cat in rules, f"Missing routing rule for {cat}"

    def test_all_rule_skills_map_to_registry(self):
        loader = RoutingRulesLoader()
        rules = loader.load()
        registry = make_registry_with_all_skills()
        for cat, rule in rules.items():
            primary = rule.get("primary_skill")
            if primary:
                assert registry.get_skill(primary) is not None, f"Skill '{primary}' not in registry for category '{cat}'"
            for secondary in rule.get("secondary_skills", []):
                assert registry.get_skill(secondary) is not None, f"Secondary skill '{secondary}' not in registry for category '{cat}'"

    def test_each_category_selects_primary_skill(self):
        registry = make_registry_with_all_skills()
        router = SkillRouter(registry=registry)
        for cat in ALL_CATEGORIES:
            ctx = RoutingContext(
                prompt=f"test {cat}",
                attack_categories=[cat],
                policy_action="RESTRICT",
                risk_score=50,
            )
            result = router.route(ctx)
            assert cat in result.selected_skills, f"Category '{cat}' should select skill '{cat}'"
            assert cat in result.executed_skills, f"Skill '{cat}' should be executed"

    def test_routing_result_type(self):
        registry = make_registry_with_all_skills()
        router = SkillRouter(registry=registry)
        for cat in ALL_CATEGORIES:
            ctx = RoutingContext(
                prompt=f"test {cat}",
                attack_categories=[cat],
                policy_action="RESTRICT",
                risk_score=50,
            )
            result = router.route(ctx)
            assert isinstance(result, RoutingResult)

    def test_rules_define_priority(self):
        loader = RoutingRulesLoader()
        rules = loader.load()
        for cat, rule in rules.items():
            assert "priority" in rule, f"Rule for '{cat}' missing priority"
            assert isinstance(rule["priority"], int), f"Priority for '{cat}' must be int"

    def test_rules_define_min_policy_action(self):
        loader = RoutingRulesLoader()
        rules = loader.load()
        for cat, rule in rules.items():
            assert "min_policy_action" in rule, f"Rule for '{cat}' missing min_policy_action"

    def test_secondary_skills_are_loaded(self):
        registry = make_registry_with_all_skills()
        router = SkillRouter(registry=registry)
        ctx = RoutingContext(
            prompt="multi_turn_probe test",
            attack_categories=["multi_turn_probe"],
            policy_action="RESTRICT",
            risk_score=50,
        )
        result = router.route(ctx)
        assert "multi_turn_probe" in result.selected_skills
        assert "partial_disclosure" in result.selected_skills
        assert "data_reconstruction" in result.selected_skills

    def test_priority_from_rules_takes_effect(self):
        registry = make_registry_with_all_skills()
        router = SkillRouter(registry=registry)
        ctx = RoutingContext(
            prompt="multiple categories",
            attack_categories=["format_smuggling", "system_prompt_extraction"],
            policy_action="RESTRICT",
            risk_score=50,
        )
        result = router.route(ctx)
        sys_idx = result.selected_skills.index("system_prompt_extraction")
        fmt_idx = result.selected_skills.index("format_smuggling")
        assert sys_idx < fmt_idx, "system_prompt_extraction (priority 100) should come before format_smuggling (priority 60)"
