from .leakage_result import LeakageMatch
from . import leakage_types as lt


SEMANTIC_HIGH_THRESHOLD = 2


class SemanticLeakDetector:
    def detect(self, output_text: str, asset: dict, context: dict | None = None) -> list[LeakageMatch]:
        aliases = asset.get("aliases", [])
        if not aliases:
            return []
        output_lower = output_text.lower()
        matched_terms = []
        for alias in aliases:
            if alias and alias.lower() in output_lower:
                matched_terms.append(alias)
        if matched_terms:
            count = len(matched_terms)
            if count >= SEMANTIC_HIGH_THRESHOLD:
                severity = lt.SEVERITY_HIGH
            else:
                severity = lt.SEVERITY_MEDIUM
            confidence = round(min(1.0, count / max(len(aliases), 1) + 0.2), 2)
            return [
                LeakageMatch(
                    asset_id=asset.get("asset_id", ""),
                    asset_name=asset.get("name", ""),
                    leak_type=lt.SEMANTIC_LEAK,
                    match_type="semantic_alias",
                    severity=severity,
                    confidence=confidence,
                    matched_text=matched_terms[0],
                    matched_fragments=matched_terms,
                )
            ]
        return []
