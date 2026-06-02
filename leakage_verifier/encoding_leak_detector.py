import base64
import re
from urllib.parse import unquote
from .leakage_result import LeakageMatch
from . import leakage_types as lt


def rot13(text: str) -> str:
    result = []
    for c in text:
        if "a" <= c <= "z":
            result.append(chr((ord(c) - ord("a") + 13) % 26 + ord("a")))
        elif "A" <= c <= "Z":
            result.append(chr((ord(c) - ord("A") + 13) % 26 + ord("A")))
        else:
            result.append(c)
    return "".join(result)


class EncodingLeakDetector:
    def detect(self, output_text: str, asset: dict, context: dict | None = None) -> list[LeakageMatch]:
        value = asset.get("value", "")
        if not value:
            return []
        output_lower = output_text.lower()
        value_lower = value.lower()
        matches = []

        try:
            b64_encoded = base64.b64encode(value.encode()).decode()
            if b64_encoded.lower() in output_lower:
                matches.append(LeakageMatch(
                    asset_id=asset.get("asset_id", ""),
                    asset_name=asset.get("name", ""),
                    leak_type=lt.ENCODING_LEAK,
                    match_type="base64",
                    severity=lt.SEVERITY_CRITICAL,
                    confidence=1.0,
                    matched_text=b64_encoded,
                ))
        except Exception:
            pass

        hex_encoded = value.encode().hex()
        if hex_encoded.lower() in output_lower:
            matches.append(LeakageMatch(
                asset_id=asset.get("asset_id", ""),
                asset_name=asset.get("name", ""),
                leak_type=lt.ENCODING_LEAK,
                match_type="hex",
                severity=lt.SEVERITY_CRITICAL,
                confidence=1.0,
                matched_text=hex_encoded,
            ))

        try:
            url_encoded = _url_encode(value)
            if url_encoded.lower() in output_lower:
                matches.append(LeakageMatch(
                    asset_id=asset.get("asset_id", ""),
                    asset_name=asset.get("name", ""),
                    leak_type=lt.ENCODING_LEAK,
                    match_type="url_encoding",
                    severity=lt.SEVERITY_CRITICAL,
                    confidence=1.0,
                    matched_text=url_encoded,
                ))
        except Exception:
            pass

        rot13_encoded = rot13(value)
        if rot13_encoded.lower() in output_lower:
            matches.append(LeakageMatch(
                asset_id=asset.get("asset_id", ""),
                asset_name=asset.get("name", ""),
                leak_type=lt.ENCODING_LEAK,
                match_type="rot13",
                severity=lt.SEVERITY_CRITICAL,
                confidence=1.0,
                matched_text=rot13_encoded,
            ))

        return matches


def _url_encode(text: str) -> str:
    result = []
    for c in text:
        if c.isalnum() or c in "._-~":
            result.append(c)
        else:
            result.append(f"%{ord(c):02X}")
    return "".join(result)
