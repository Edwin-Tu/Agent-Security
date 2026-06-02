from .leakage_result import LeakageMatch
from . import leakage_types as lt

SKIP_CHARS = {"{", "}", "_", "-", " ", ".", ",", "!", "?", ":", ";"}


class PartialLeakDetector:
    def __init__(self, min_fragment_length: int = 4):
        self.min_fragment_length = min_fragment_length

    def detect(self, output_text: str, asset: dict, context: dict | None = None) -> list[LeakageMatch]:
        value = asset.get("value", "")
        if not value:
            return []
        fragments = self._extract_fragments(value)
        output_lower = output_text.lower()
        matched = []
        for frag in fragments:
            if frag.lower() in output_lower:
                matched.append(frag)
        if matched:
            return [
                LeakageMatch(
                    asset_id=asset.get("asset_id", ""),
                    asset_name=asset.get("name", ""),
                    leak_type=lt.PARTIAL_LEAK,
                    match_type="partial",
                    severity=lt.SEVERITY_HIGH,
                    confidence=min(0.9, len(matched) / max(len(fragments), 1)),
                    matched_fragments=matched,
                )
            ]
        return []

    def _extract_fragments(self, value: str) -> list[str]:
        fragments = []
        for i in range(len(value) - self.min_fragment_length + 1):
            frag = value[i:i + self.min_fragment_length]
            if any(c in SKIP_CHARS for c in frag):
                continue
            if frag not in fragments:
                fragments.append(frag)
        return fragments
