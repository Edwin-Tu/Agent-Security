import base64
import binascii
import re
import urllib.parse


def _is_readable_text(text: str) -> bool:
    if not text:
        return False
    if any(c in text for c in "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f"):
        return False
    return all(ch.isprintable() or ch.isspace() for ch in text)


def _is_base64_string(text: str) -> bool:
    text = text.strip()
    return bool(re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", text)) and len(text) % 4 == 0


def _is_hex_string(text: str) -> bool:
    return bool(re.fullmatch(r"[0-9A-Fa-f]+", text)) and len(text) % 2 == 0 and len(text) >= 4


def probe_encoded_candidates(text: str) -> tuple[list[str], list[str]]:
    if not isinstance(text, str):
        text = str(text)

    candidates: list[str] = []
    flags: list[str] = []
    trimmed = text.strip()

    if _is_base64_string(trimmed):
        try:
            decoded = base64.b64decode(trimmed, validate=True)
            decoded_text = decoded.decode("utf-8")
            if _is_readable_text(decoded_text):
                candidates.append(decoded_text)
                flags.append("possible_base64_detected")
        except (binascii.Error, UnicodeDecodeError):
            pass

    if "%" in trimmed or "+" in trimmed:
        decoded = urllib.parse.unquote_plus(trimmed)
        if decoded != trimmed and _is_readable_text(decoded):
            candidates.append(decoded)
            flags.append("possible_url_encoding_detected")

    hex_text = re.sub(r"\s+", "", trimmed)
    if _is_hex_string(hex_text):
        try:
            decoded = binascii.unhexlify(hex_text)
            decoded_text = decoded.decode("utf-8")
            if _is_readable_text(decoded_text):
                candidates.append(decoded_text)
                flags.append("possible_hex_detected")
        except (binascii.Error, UnicodeDecodeError):
            pass

    unique_candidates = list(dict.fromkeys(candidates))
    unique_flags = list(dict.fromkeys(flags))
    return unique_candidates, unique_flags
