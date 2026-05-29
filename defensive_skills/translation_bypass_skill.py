from .base_skill import BaseSkill
from .skill_models import SkillInput, DetectionResult, DefenseResult


class TranslationBypassSkill(BaseSkill):
    skill_name = "TranslationBypassSkill"
    attack_categories = ["translation_bypass"]

    PATTERNS = [
        "翻成英文", "翻成中文", "翻成日文", "翻成韓文",
        "用英文寫", "用日文寫", "用韓文寫", "用法文寫",
        "換成中文", "換成英文",
        "translate", "in english", "in chinese",
        "in japanese", "in french", "in korean",
        "翻訳", "번역",
        "不要原文", "不要用原文",
    ]

    def detect(self, skill_input: SkillInput) -> DetectionResult:
        result = self._match_patterns(skill_input.normalized_prompt, self.PATTERNS)
        if result:
            return result
        return DetectionResult(matched=False)

    def defend(self, skill_input: SkillInput, detection_result: DetectionResult) -> DefenseResult:
        return self._build_defense(
            detection=detection_result,
            action="RESTRICT",
            safe_prompt="[SecretGuard Restricted] 偵測到翻譯繞過嘗試，已限制。",
            response_message="禁止透過翻譯方式輸出敏感資訊。",
            restrictions=["no_translation_bypass"],
            runtime_checks=["translation_secret_check"],
        )
