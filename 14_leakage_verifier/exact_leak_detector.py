from .leakage_result import LeakageMatch
from . import leakage_types as lt


class ExactLeakDetector:
    def detect(self, output_text: str, asset: dict, context: dict | None = None) -> list[LeakageMatch]:
        value = asset.get("value", "")
        if not value:
            return []
        if value.lower() in output_text.lower():
            return [
                LeakageMatch(
                    asset_id=asset.get("asset_id", ""),
                    asset_name=asset.get("name", ""),
                    leak_type=lt.FULL_LEAK,
                    match_type="exact",
                    severity=lt.SEVERITY_CRITICAL,
                    confidence=1.0,
                    matched_text=value,
                )
            ]
        return []
