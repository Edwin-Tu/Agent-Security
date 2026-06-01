from .base_skill import BaseSkill
from .skill_models import SkillInput, DetectionResult, DefenseResult


class EncodingBypassSkill(BaseSkill):
    skill_name = "EncodingBypassSkill"
    attack_categories = ["encoding_bypass"]

    PATTERNS = [
        "base64 輸出", "用 base64", "base64 編碼",
        "轉成 hex", "hex 編碼", "hex 輸出",
        "rot13", "rot 13",
        "morse 編碼", "用摩斯電碼",
        "用 base64", "編碼成 base64",
        "encode as base64", "encode the secret",
        "base64 encode", "hex encode",
        "url encode", "percent encoding",
        "unicode escape",
    ]

    def detect(self, skill_input: SkillInput) -> DetectionResult:
        text = skill_input.normalized_prompt.lower()
        result = self._match_patterns(skill_input.normalized_prompt, self.PATTERNS)
        if result:
            return result
        if "rot13" in text or "rot 13" in text:
            return DetectionResult(
                matched=True,
                confidence=0.85,
                matched_rules=["encoding_bypass"],
                reasons=["Matched encoding pattern: rot13"],
                risk_tags=["encoding_bypass"],
            )
        return DetectionResult(matched=False)

    def defend(self, skill_input: SkillInput, detection_result: DetectionResult) -> DefenseResult:
        return self._build_defense(
            detection=detection_result,
            action="RESTRICT",
            safe_prompt="[SecretGuard Restricted] 偵測到編碼繞過嘗試，已限制。",
            response_message="禁止使用編碼方式輸出敏感資訊。",
            restrictions=["no_encoding_bypass"],
            runtime_checks=["encoded_secret_check"],
        )
