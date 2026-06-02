import re
from typing import Optional


class ReconstructionMatcher:
    @staticmethod
    def match(text: str, asset: dict) -> Optional[dict]:
        if not text or not asset:
            return None
        value = asset.get("value", "")
        if not value:
            return None

        text_clean = re.sub(r"\s+", "", text.lower())
        value_clean = re.sub(r"\s+", "", value.lower())
        if not value_clean:
            return None

        matched_segments = []
        total_chars = len(value_clean)
        matched_chars = 0

        if len(value_clean) < 3:
            return None

        for length in range(len(value_clean), 2, -1):
            for start in range(len(value_clean) - length + 1):
                segment = value_clean[start:start + length]
                if segment in text_clean:
                    matched_segments.append(segment)
                    matched_chars = max(matched_chars, length)
                    break
            if matched_chars >= total_chars * 0.8:
                break

        if matched_chars >= 3:
            coverage = matched_chars / max(total_chars, 1)
            risk = "high" if coverage >= 0.8 else "medium" if coverage >= 0.5 else "low"
            return {
                "matched": True,
                "matched_segments": matched_segments[:5],
                "longest_match": matched_chars,
                "total_length": total_chars,
                "coverage_ratio": round(coverage, 2),
                "risk_level": risk,
            }

        chars_in_text = sum(1 for c in value_clean if c in text_clean)
        char_coverage = chars_in_text / max(total_chars, 1)
        if char_coverage >= 0.7 and total_chars >= 5:
            return {
                "matched": True,
                "matched_segments": [],
                "longest_match": 0,
                "total_length": total_chars,
                "coverage_ratio": round(char_coverage, 2),
                "risk_level": "medium" if char_coverage >= 0.8 else "low",
            }

        return None
