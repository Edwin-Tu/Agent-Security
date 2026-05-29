from .base_skill import BaseSkill
from .skill_models import SkillInput, DetectionResult, DefenseResult


class MultiTurnProbeSkill(BaseSkill):
    skill_name = "MultiTurnProbeSkill"
    attack_categories = ["multi_turn_probe"]

    PROBE_PATTERNS = [
        "長度", "長度是多少",
        "第一個字元", "第一個字母", "第一個字",
        "最後一個字元", "最後一個字母",
        "前幾碼", "前兩碼", "前三碼", "前一碼",
        "後幾碼", "後兩碼",
        "逐字", "一個字一個字",
        "first character", "last character",
        "length", "how long",
        "字元數", "字數",
    ]

    def detect(self, skill_input: SkillInput) -> DetectionResult:
        history = skill_input.session_context.get("history", [])
        probe_count = 0
        for h in history:
            h_lower = h.lower()
            for p in self.PROBE_PATTERNS:
                if p in h_lower:
                    probe_count += 1
                    break

        current_text = skill_input.normalized_prompt.lower()
        current_is_probe = any(p in current_text for p in self.PROBE_PATTERNS)

        total_probes = probe_count + (1 if current_is_probe else 0)

        if total_probes >= 3:
            return DetectionResult(
                matched=True,
                confidence=0.9,
                matched_rules=["multi_turn_probe"],
                reasons=[f"Detected {total_probes} probe patterns across turns"],
                risk_tags=["multi_turn_probe"],
            )

        if current_is_probe and probe_count >= 2:
            return DetectionResult(
                matched=True,
                confidence=0.85,
                matched_rules=["multi_turn_probe"],
                reasons=[f"Detected {probe_count} prior probes plus current probe"],
                risk_tags=["multi_turn_probe"],
            )

        return DetectionResult(matched=False)

    def defend(self, skill_input: SkillInput, detection_result: DetectionResult) -> DefenseResult:
        return self._build_defense(
            detection=detection_result,
            action="ESCALATE",
            safe_prompt="[SecretGuard Escalated] 偵測到多輪探測攻擊，已升級處理。",
            response_message="偵測到多輪敏感資訊探測行為，已記錄並上報。",
            restrictions=["no_multi_turn_probe"],
            runtime_checks=["session_risk_check", "partial_secret_check"],
        )
