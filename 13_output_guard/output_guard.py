from .pattern_detector import PatternDetector
from .asset_output_matcher import AssetOutputMatcher
from .redactor import Redactor
from .output_guard_result import OutputGuardResult
from . import severity as sev


class OutputGuard:
    def __init__(self):
        self.pattern_detector = PatternDetector()
        self.asset_matcher = AssetOutputMatcher()
        self.redactor = Redactor()

    def inspect(self, text: str, protected_assets: list[dict] | None = None) -> OutputGuardResult:
        if not text:
            return OutputGuardResult(
                original_output=text,
                safe_output=text,
                action=sev.ALLOW,
                is_blocked=False,
                is_redacted=False,
                leakage_detected=False,
                risk_level=sev.NO_LEAK,
            )

        pattern_findings = self.pattern_detector.detect(text)

        asset_result = {
            "matched_assets": [],
            "matched_patterns": [],
            "leakage_detected": False,
            "severity": sev.NO_LEAK,
            "action": sev.ALLOW,
        }
        if protected_assets:
            asset_result = self.asset_matcher.match(text, protected_assets)

        matched_patterns = list(set(f["name"] for f in pattern_findings))
        matched_patterns.extend(asset_result.get("matched_patterns", []))

        all_findings = list(pattern_findings)

        leakage_detected = len(pattern_findings) > 0 or asset_result.get("leakage_detected", False)

        severity = sev.NO_LEAK
        actions = set()
        for f in pattern_findings:
            sev_level = f.get("severity", sev.FULL_LEAK)
            action = f.get("action", sev.REDACT)
            if sev.SEVERITY_ORDER.get(sev_level, 0) > sev.SEVERITY_ORDER.get(severity, 0):
                severity = sev_level
            actions.add(action)

        asset_sev = asset_result.get("severity", sev.NO_LEAK)
        if sev.SEVERITY_ORDER.get(asset_sev, 0) > sev.SEVERITY_ORDER.get(severity, 0):
            severity = asset_sev
        actions.add(asset_result.get("action", sev.ALLOW))

        if sev.BLOCK in actions:
            action = sev.BLOCK
        elif sev.REDACT in actions:
            action = sev.REDACT
        else:
            action = sev.ALLOW

        safe_output = text
        reasons = []
        matched_assets = list(set(asset_result.get("matched_assets", [])))

        if pattern_findings:
            for f in pattern_findings:
                reasons.append(f"Detected {f['type']}: {f['name']}")

        if matched_assets:
            for a in matched_assets:
                reasons.append(f"Protected asset matched: {a}")

        if pattern_findings or asset_result.get("matched_assets"):
            if action == sev.BLOCK:
                for f in pattern_findings:
                    safe_output = self.redactor.redact_patterns(safe_output, [f])
                if matched_assets and protected_assets:
                    for a_id in matched_assets:
                        for asset in protected_assets:
                            if asset.get("asset_id") == a_id:
                                val = asset.get("value", "")
                                safe_output = self.redactor.redact_asset(safe_output, val)
            elif action == sev.REDACT:
                for f in pattern_findings:
                    safe_output = self.redactor.redact_patterns(safe_output, [f])
                if matched_assets and protected_assets:
                    for a_id in matched_assets:
                        for asset in protected_assets:
                            val = asset.get("value", "")
                            safe_output = self.redactor.redact_asset(safe_output, val)
                            for alias in asset.get("aliases", []):
                                if alias:
                                    safe_output = self.redactor.redact_asset(safe_output, alias)

        if asset_result.get("severity") == sev.PARTIAL_LEAK and not pattern_findings:
            for a_id in matched_assets:
                if protected_assets:
                    for asset in protected_assets:
                        if asset.get("asset_id") == a_id:
                            val = asset.get("value", "")
                            safe_output = self.redactor.redact_asset_partial(safe_output, val)

        is_blocked = action == sev.BLOCK
        is_redacted = action == sev.REDACT and safe_output != text

        return OutputGuardResult(
            original_output=text,
            safe_output=safe_output,
            action=action,
            is_blocked=is_blocked,
            is_redacted=is_redacted,
            leakage_detected=leakage_detected,
            matched_patterns=matched_patterns,
            matched_assets=matched_assets,
            risk_level=severity,
            reasons=reasons,
        )
