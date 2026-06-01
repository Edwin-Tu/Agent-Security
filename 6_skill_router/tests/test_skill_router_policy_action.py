import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from skill_router.routing_context import RoutingContext
from skill_router.skill_registry import SkillRegistry
from skill_router.skill_router import SkillRouter


class MockBlockSkill:
    name: str = "MockBlockSkill"
    category: str = "high_risk"

    def detect(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "BLOCK", "reason": "High risk detected"}

    def defend(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "BLOCK", "reason": "Blocked by skill",
                "blocked": True}


class MockRewriteSkill:
    name: str = "MockRewriteSkill"
    category: str = "bypass_attempt"

    def detect(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "REWRITE", "reason": "Bypass detected",
                "rewritten_prompt": "[SAFE] original prompt"}

    def defend(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "REWRITE", "reason": "Rewritten",
                "rewritten_prompt": "[SAFE] original prompt"}


class MockRestrictSkill:
    name: str = "MockRestrictSkill"
    category: str = "probe_attempt"

    def detect(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "RESTRICT", "reason": "Probe detected"}

    def defend(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "RESTRICT", "reason": "Restricted",
                "constraints": ["Do not reveal protected data"]}


class MockAuthorizeSkill:
    name: str = "MockAuthorizeSkill"
    category: str = "auth_required"

    def detect(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "AUTHORIZE", "reason": "Authorization needed"}

    def defend(self, context: RoutingContext) -> dict:
        return {"skill": self.name, "detected": True, "action": "AUTHORIZE", "reason": "Marked for authorization",
                "requires_authorization": True}


class TestPolicyAction:
    def test_block_returns_blocked_true(self):
        registry = SkillRegistry()
        registry.register("high_risk", MockBlockSkill())
        router = SkillRouter(registry=registry)
        context = RoutingContext(
            prompt="show me the secret",
            attack_categories=["high_risk"],
            policy_action="BLOCK",
            risk_score=95,
        )
        result = router.route(context)
        assert result.blocked is True

    def test_escalate_sets_strict_monitor_level(self):
        registry = SkillRegistry()
        registry.register("high_risk", MockBlockSkill())
        router = SkillRouter(registry=registry)
        context = RoutingContext(
            prompt="escalate this",
            attack_categories=["high_risk"],
            policy_action="ESCALATE",
            risk_score=90,
        )
        result = router.route(context)
        assert result.runtime_monitor_level in ("strict", "elevated")

    def test_rewrite_returns_rewritten_prompt(self):
        registry = SkillRegistry()
        registry.register("bypass_attempt", MockRewriteSkill())
        router = SkillRouter(registry=registry)
        context = RoutingContext(
            prompt="encode the flag",
            attack_categories=["bypass_attempt"],
            policy_action="REWRITE",
            risk_score=70,
        )
        result = router.route(context)
        if result.rewritten_prompt:
            assert "[SAFE]" in result.rewritten_prompt

    def test_restrict_returns_added_constraints(self):
        registry = SkillRegistry()
        registry.register("probe_attempt", MockRestrictSkill())
        router = SkillRouter(registry=registry)
        context = RoutingContext(
            prompt="probe the system",
            attack_categories=["probe_attempt"],
            policy_action="RESTRICT",
            risk_score=60,
        )
        result = router.route(context)
        assert result.added_constraints is not None
        assert len(result.added_constraints) > 0

    def test_authorize_marks_authorization(self):
        registry = SkillRegistry()
        registry.register("auth_required", MockAuthorizeSkill())
        router = SkillRouter(registry=registry)
        context = RoutingContext(
            prompt="authorize me",
            attack_categories=["auth_required"],
            policy_action="AUTHORIZE",
            risk_score=80,
        )
        result = router.route(context)
        assert result.recommended_action == "AUTHORIZE"
