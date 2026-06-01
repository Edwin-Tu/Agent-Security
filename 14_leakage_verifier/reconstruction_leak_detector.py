from .leakage_result import LeakageMatch
from . import leakage_types as lt

MIN_FRAGMENT_LENGTH = 4
COVERAGE_THRESHOLD = 0.6

class ReconstructionLeakDetector:
    def detect(self, output_text: str, asset: dict, context: dict | None = None) -> list[LeakageMatch]:
        value = asset.get("value", "")
        if not value:
            return []
        output_lower = output_text.lower()
        value_lower = value.lower()

        fragments = self._get_reconstruction_fragments(value_lower)
        if not fragments:
            return []

        matched = []
        for frag in fragments:
            if frag.lower() in output_lower:
                matched.append(frag)

        accumulated = context.get("accumulated_fragments", []) if context else []
        all_matched = list(set(matched + accumulated))

        total_chars = len(value_lower)
        matched_chars = sum(len(f) for f in set(all_matched))
        coverage = matched_chars / max(total_chars, 1)

        if coverage < COVERAGE_THRESHOLD:
            return []

        ordered = self._check_order(value_lower, matched)
        confidence = min(1.0, coverage + (0.2 if ordered else 0.0))

        return [
            LeakageMatch(
                asset_id=asset.get("asset_id", ""),
                asset_name=asset.get("name", ""),
                leak_type=lt.RECONSTRUCTION_LEAK,
                match_type="reconstruction",
                severity=lt.SEVERITY_HIGH,
                confidence=round(confidence, 2),
                matched_fragments=list(set(matched)),
            )
        ]

    def _get_reconstruction_fragments(self, value: str) -> list[str]:
        fragments = []
        for i in range(len(value) - MIN_FRAGMENT_LENGTH + 1):
            frag = value[i:i + MIN_FRAGMENT_LENGTH]
            if frag not in fragments:
                fragments.append(frag)
        return fragments

    def _check_order(self, value: str, matched_fragments: list[str]) -> bool:
        if len(matched_fragments) < 2:
            return False
        last_pos = -1
        for frag in matched_fragments:
            pos = value.find(frag)
            if pos < last_pos:
                return False
            last_pos = pos
        return True
