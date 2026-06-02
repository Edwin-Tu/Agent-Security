from .base_skill import BaseSkill
from .skill_models import SkillInput, DetectionResult, DefenseResult


class PartialDisclosureSkill(BaseSkill):
    skill_name = "PartialDisclosureSkill"
    attack_categories = ["partial_disclosure"]

    PATTERNS = [
        "前三碼", "前兩碼", "前一碼", "前幾碼",
        "最後一碼", "最後兩碼", "最後三碼", "最後四碼", "後幾碼",
        "第一個字元", "第一個字母", "第一個字",
        "最後一個字元", "最後一個字母", "最後一個字",
        "一個字一個字", "逐字", "一個字母一個字母",
        "first character", "last character",
        "first letter", "last letter",
        "one letter at a time", "one character at a time",
        "逐個字元", "分段",
    ]

    def detect(self, skill_input: SkillInput) -> DetectionResult:
        result = self._match_patterns(skill_input.normalized_prompt, self.PATTERNS)
        if result:
            return result
        return DetectionResult(matched=False)

    def defend(self, skill_input: SkillInput, detection_result: DetectionResult) -> DefenseResult:
        return self._build_defense(
            detection=detection_result,
            action="BLOCK",
            safe_prompt="[SecretGuard Blocked] 偵測到部分揭露嘗試，已阻擋。",
            response_message="禁止分段揭露敏感資訊。",
            restrictions=["no_partial_disclosure"],
            runtime_checks=["partial_secret_check"],
        )
