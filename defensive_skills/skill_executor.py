from .base_skill import BaseSkill
from .skill_models import SkillInput, DefenseResult, highest_severity_action, merge_unique


class SkillExecutor:
    def execute(self, skill_input: SkillInput, skills: list[BaseSkill]) -> DefenseResult:
        matched_results = []

        for skill in skills:
            detection = skill.detect(skill_input)
            if detection.matched:
                defense = skill.defend(skill_input, detection)
                matched_results.append((skill, defense))

        if not matched_results:
            return DefenseResult(action="ALLOW")

        actions = []
        all_evidence = {}
        all_risk_tags = []
        all_runtime_checks = []
        all_restrictions = []
        safe_prompt = None
        response_message = None

        for skill, defense in matched_results:
            actions.append(defense.action)
            all_evidence[skill.skill_name] = {
                "action": defense.action,
                "risk_tags": defense.risk_tags,
                "runtime_checks": defense.runtime_checks,
                "evidence": defense.evidence,
            }
            all_risk_tags.extend(defense.risk_tags)
            all_runtime_checks.extend(defense.runtime_checks)
            all_restrictions.extend(defense.restrictions)
            if defense.safe_prompt:
                safe_prompt = defense.safe_prompt
            if defense.response_message:
                response_message = defense.response_message

        final_action = highest_severity_action(actions)

        return DefenseResult(
            action=final_action,
            safe_prompt=safe_prompt,
            response_message=response_message,
            restrictions=merge_unique(all_restrictions),
            risk_tags=merge_unique(all_risk_tags),
            runtime_checks=merge_unique(all_runtime_checks),
            evidence=all_evidence,
        )
