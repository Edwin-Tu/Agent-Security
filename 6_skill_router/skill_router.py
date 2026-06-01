from .routing_context import RoutingContext
from .routing_result import RoutingResult
from .skill_registry import SkillRegistry
from .routing_rules_loader import RoutingRulesLoader


POLICY_ACTION_MONITOR_MAP = {
    "ALLOW": "normal",
    "WARN": "normal",
    "REWRITE": "normal",
    "RESTRICT": "normal",
    "BLOCK": "strict",
    "AUTHORIZE": "elevated",
    "ESCALATE": "elevated",
}

HIGH_RISK_ACTIONS = {"BLOCK", "ESCALATE"}


class SkillRouter:
    def __init__(self, registry: SkillRegistry | None = None, rules_loader: RoutingRulesLoader | None = None):
        self.registry = registry or SkillRegistry()
        self.rules_loader = rules_loader or RoutingRulesLoader()
        self._rules = {}
        self._load_rules()

    def _load_rules(self):
        try:
            self._rules = self.rules_loader.load()
        except (FileNotFoundError, ValueError):
            self._rules = {}

    def route(self, context: RoutingContext) -> RoutingResult:
        categories = context.attack_categories
        policy_action = context.policy_action

        selected_skills = self._select_skills(categories, policy_action)
        deduplicated = self._deduplicate(selected_skills)
        sorted_skills = self._sort_by_priority(deduplicated)

        executed_skills, skill_results = self._execute_skills(sorted_skills, context)

        recommended_action = self._determine_recommended_action(policy_action, skill_results)
        rewritten_prompt = self._merge_rewritten_prompts(skill_results)
        added_constraints = self._merge_constraints(skill_results)
        blocked = self._is_blocked(policy_action, skill_results)
        runtime_monitor_level = self._determine_monitor_level(policy_action, skill_results)
        reasons = self._build_reasons(skill_results, categories)
        unknown = self._get_unknown_categories(categories)
        for cat in unknown:
            reasons.append(f"Unknown attack category: {cat}")

        return RoutingResult(
            selected_skills=sorted_skills,
            executed_skills=executed_skills,
            skill_results=skill_results,
            recommended_action=recommended_action,
            rewritten_prompt=rewritten_prompt,
            added_constraints=added_constraints or None,
            runtime_monitor_level=runtime_monitor_level,
            blocked=blocked,
            reasons=reasons or None,
        )

    def _select_skills(self, categories: list[str], policy_action: str) -> list[str]:
        skills = []
        for cat in categories:
            rule = self._rules.get(cat)
            if rule:
                primary = rule.get("primary_skill")
                if primary:
                    skills.append(primary)
                    priority = rule.get("priority")
                    if priority is not None:
                        self.registry.set_priority(primary, priority)
                for secondary in rule.get("secondary_skills", []):
                    skills.append(secondary)
                    priority = rule.get("priority", 50) - 5
                    self.registry.set_priority(secondary, priority)
            else:
                registry_skills = self.registry.get(cat)
                for skill in registry_skills:
                    skills.append(skill.name)
        return skills

    def _deduplicate(self, skills: list[str]) -> list[str]:
        seen = set()
        result = []
        for s in skills:
            if s not in seen:
                seen.add(s)
                result.append(s)
        return result

    def _sort_by_priority(self, skills: list[str]) -> list[str]:
        return sorted(
            skills,
            key=lambda name: self.registry.get_priority(name),
            reverse=True,
        )

    def _execute_skills(self, skill_names: list[str], context: RoutingContext) -> tuple[list[str], list[dict]]:
        executed = []
        results = []
        for name in skill_names:
            skill = self.registry.get_skill(name)
            if skill is None:
                continue
            detect_result = skill.detect(context)
            if detect_result.get("detected"):
                defend_result = skill.defend(context)
                merged = dict(detect_result)
                merged.update(defend_result)
                merged["skill"] = merged.get("skill", name)
                results.append(merged)
            else:
                results.append(detect_result)
            executed.append(name)
        return executed, results

    def _determine_recommended_action(self, policy_action: str, skill_results: list[dict]) -> str:
        action_priority = ["ALLOW", "WARN", "REWRITE", "RESTRICT", "AUTHORIZE", "BLOCK", "ESCALATE"]
        current_priority = action_priority.index(policy_action) if policy_action in action_priority else 0
        for r in skill_results:
            action = r.get("action", "ALLOW")
            if action in action_priority:
                p = action_priority.index(action)
                if p > current_priority:
                    current_priority = p
        return action_priority[current_priority]

    def _merge_rewritten_prompts(self, skill_results: list[dict]) -> str | None:
        for r in skill_results:
            prompt = r.get("rewritten_prompt")
            if prompt:
                return prompt
        return None

    def _merge_constraints(self, skill_results: list[dict]) -> list[str]:
        all_constraints = []
        seen = set()
        for r in skill_results:
            for c in r.get("constraints", []):
                if c not in seen:
                    seen.add(c)
                    all_constraints.append(c)
        return all_constraints

    def _is_blocked(self, policy_action: str, skill_results: list[dict]) -> bool:
        if policy_action == "BLOCK":
            return True
        for r in skill_results:
            if r.get("blocked") or r.get("action") == "BLOCK":
                return True
        return False

    def _determine_monitor_level(self, policy_action: str, skill_results: list[dict]) -> str:
        base = POLICY_ACTION_MONITOR_MAP.get(policy_action, "normal")
        for r in skill_results:
            action = r.get("action", "")
            action_level = POLICY_ACTION_MONITOR_MAP.get(action, "normal")
            level_order = ["normal", "elevated", "strict"]
            if level_order.index(action_level) > level_order.index(base):
                base = action_level
        return base

    def _build_reasons(self, skill_results: list[dict], categories: list[str]) -> list[str]:
        reasons = []
        for r in skill_results:
            reason = r.get("reason")
            if reason:
                reasons.append(reason)
        return reasons

    def _get_unknown_categories(self, categories: list[str]) -> list[str]:
        unknown = []
        for cat in categories:
            rule = self._rules.get(cat)
            if rule:
                primary = rule.get("primary_skill")
                if primary and not self.registry.get_skill(primary):
                    unknown.append(cat)
                continue
            if not self.registry.has(cat):
                unknown.append(cat)
        return unknown
