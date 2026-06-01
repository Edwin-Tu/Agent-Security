from input_guard.detectors.keyword_detector import KeywordDetector
from input_guard.detectors.suspicious_format_detector import SuspiciousFormatDetector
from input_guard.detectors.asset_request_detector import AssetRequestDetector
from input_guard.detectors.override_detector import OverrideDetector
from input_guard.detectors.role_claim_detector import RoleClaimDetector
from input_guard.detectors.encoding_hint_detector import EncodingHintDetector


class InputGuard:
    def __init__(self):
        self.detectors = {
            "keyword": KeywordDetector(),
            "suspicious_format": SuspiciousFormatDetector(),
            "asset_request": AssetRequestDetector(),
            "override": OverrideDetector(),
            "role_claim": RoleClaimDetector(),
            "encoding_hint": EncodingHintDetector(),
        }

    def check(self, text: str) -> dict:
        if not text or not text.strip():
            return {
                "allow": True,
                "score_hint": 0,
                "matched_rules": [],
                "detected_assets": [],
                "claimed_role": None,
                "requires_authorization_check": False,
                "normalized_excerpt": "",
                "recommended_action": "allow",
            }

        all_rules = []
        all_assets = []
        claimed_role = None
        requires_auth = False

        for name, detector in self.detectors.items():
            result = detector.detect(text)
            if result.get("matched"):
                all_rules.extend(result.get("rules", []))

                assets = result.get("detected_assets", [])
                if assets:
                    all_assets.extend(assets)

                role = result.get("claimed_role")
                if role:
                    claimed_role = role

                if result.get("requires_authorization_check"):
                    requires_auth = True

        all_rules = list(set(all_rules))
        all_assets = list(set(all_assets))

        score_hint = self._compute_score(all_rules, all_assets, requires_auth)

        allow = score_hint < 40

        recommended_action = self._get_recommended_action(score_hint, all_rules)

        return {
            "allow": allow,
            "score_hint": score_hint,
            "matched_rules": sorted(all_rules),
            "detected_assets": sorted(all_assets),
            "claimed_role": claimed_role,
            "requires_authorization_check": requires_auth,
            "normalized_excerpt": text[:200],
            "recommended_action": recommended_action,
        }

    def _compute_score(self, rules: list, assets: list, requires_auth: bool) -> int:
        scores = {
            "direct_secret_request": 40,
            "instruction_override": 35,
            "system_prompt_probe": 30,
            "internal_rule_probe": 30,
            "protected_asset_mention": 30,
            "partial_disclosure": 40,
            "encoded_disclosure": 35,
            "possible_xss": 40,
            "prompt_smuggling": 35,
            "structured_leakage_request": 40,
            "suspicious_format": 20,
            "obfuscation_hint": 40,
            "encoding_hint": 30,
            "cross_language_hint": 15,
            "role_claim": 30,
        }

        base = 0
        for rule in rules:
            base += scores.get(rule, 10)

        if requires_auth:
            base += 10

        if len(assets) > 0:
            base += len(assets) * 5

        if len(rules) >= 3:
            base += 15

        return min(base, 100)

    def _get_recommended_action(self, score: int, rules: list) -> str:
        if score >= 70:
            return "block_candidate"

        if score >= 50:
            return "escalate_candidate"

        if score >= 30:
            return "monitor_candidate"

        high_risk_rules = {
            "direct_secret_request", "possible_xss", "instruction_override",
            "prompt_smuggling", "structured_leakage_request",
        }
        if any(r in high_risk_rules for r in rules):
            return "monitor_candidate"

        return "allow"
