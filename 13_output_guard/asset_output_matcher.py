from . import severity as sev


PARTIAL_MIN_LENGTH = 4


def _split_fragments(value: str, min_length: int = PARTIAL_MIN_LENGTH) -> list[str]:
    fragments = []
    for i in range(len(value) - min_length + 1):
        fragment = value[i:i + min_length]
        fragments.append(fragment)
    seen = set()
    unique = []
    for f in fragments:
        if f not in seen:
            seen.add(f)
            unique.append(f)
    return unique


class AssetOutputMatcher:
    def __init__(self):
        self.partial_min_length = PARTIAL_MIN_LENGTH

    def match(self, text: str, protected_assets: list[dict]) -> dict:
        matched_assets = []
        matched_patterns = []
        is_partial = False
        is_full = False

        for asset in protected_assets:
            value = asset.get("value", "")
            asset_id = asset.get("asset_id", "")
            risk_level = asset.get("risk_level", "medium")
            aliases = asset.get("aliases", [])
            protection_modes = asset.get("protection_modes", ["exact_match"])

            # Exact match
            if "exact_match" in protection_modes:
                if value.lower() in text.lower():
                    matched_assets.append(asset_id)
                    matched_patterns.append(f"asset_exact:{asset_id}")
                    is_full = True
                for alias in aliases:
                    if alias and alias.lower() in text.lower():
                        matched_assets.append(asset_id)
                        matched_patterns.append(f"asset_alias:{asset_id}")
                        is_full = True

            # Partial match
            if "partial_match" in protection_modes and not is_full:
                fragments = _split_fragments(value, self.partial_min_length)
                fragment_hits = []
                for frag in fragments:
                    if frag.lower() in text.lower():
                        fragment_hits.append(frag)
                if fragment_hits:
                    matched_assets.append(asset_id)
                    matched_patterns.append(f"asset_partial:{asset_id}")
                    is_partial = True

        leakage_detected = is_full or is_partial
        severity = sev.CRITICAL_LEAK if is_full else (sev.PARTIAL_LEAK if is_partial else sev.NO_LEAK)

        action = sev.SEVERITY_ACTION_MAP.get(severity, sev.ALLOW)
        if is_full and risk_level == "critical":
            severity = sev.CRITICAL_LEAK
            action = sev.BLOCK

        return {
            "matched_assets": list(set(matched_assets)),
            "matched_patterns": list(set(matched_patterns)),
            "leakage_detected": leakage_detected,
            "severity": severity,
            "action": action,
        }
