from .leakage_result import LeakageMatch
from . import leakage_types as lt


class TranslationLeakDetector:
    def detect(self, output_text: str, asset: dict, context: dict | None = None) -> list[LeakageMatch]:
        aliases = asset.get("aliases", [])
        if not aliases:
            return []
        output_lower = output_text.lower()
        matched_aliases = []
        for alias in aliases:
            if alias and alias.lower() in output_lower:
                matched_aliases.append(alias)
        if matched_aliases:
            confidence = min(1.0, len(matched_aliases) / max(len(aliases), 1) + 0.3)
            return [
                LeakageMatch(
                    asset_id=asset.get("asset_id", ""),
                    asset_name=asset.get("name", ""),
                    leak_type=lt.TRANSLATION_LEAK,
                    match_type="alias",
                    severity=lt.SEVERITY_HIGH,
                    confidence=round(confidence, 2),
                    matched_text=matched_aliases[0],
                    matched_fragments=matched_aliases,
                )
            ]
        return []
