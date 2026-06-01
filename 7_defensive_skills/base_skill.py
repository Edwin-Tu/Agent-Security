from .skill_models import SkillInput, DetectionResult, DefenseResult


class BaseSkill:
    skill_name: str = "base"
    attack_categories: list[str] = []

    def detect(self, skill_input: SkillInput) -> DetectionResult:
        raise NotImplementedError

    def defend(self, skill_input: SkillInput, detection_result: DetectionResult) -> DefenseResult:
        raise NotImplementedError

    def _match_patterns(self, text: str, patterns: list[str]) -> DetectionResult | None:
        text_lower = text.lower()
        for pattern in patterns:
            if pattern in text_lower:
                return DetectionResult(
                    matched=True,
                    confidence=0.85,
                    matched_rules=[self.attack_categories[0]] if self.attack_categories else [],
                    reasons=[f"Matched pattern: {pattern}"],
                    risk_tags=[self.attack_categories[0]] if self.attack_categories else [],
                )
        return None

    def _build_defense(
        self,
        detection: DetectionResult,
        action: str,
        safe_prompt: str,
        response_message: str,
        restrictions: list[str] | None = None,
        runtime_checks: list[str] | None = None,
    ) -> DefenseResult:
        return DefenseResult(
            action=action,
            safe_prompt=safe_prompt,
            response_message=response_message,
            restrictions=restrictions or [],
            risk_tags=detection.risk_tags[:],
            runtime_checks=runtime_checks or [],
            evidence={
                "skill_name": self.skill_name,
                "matched_rules": detection.matched_rules[:],
                "reasons": detection.reasons[:],
            },
        )
