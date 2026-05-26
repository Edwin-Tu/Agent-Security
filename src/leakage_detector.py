"""Leakage detection for SecretGuard output filtering."""

from __future__ import annotations

import re


class LeakageDetector:
    """Detect common secret leakage patterns and redact them."""

    PATTERNS = {
        "api_key": re.compile(r"(?:sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36,})"),
        "token": re.compile(r"(?:Bearer\s+[A-Za-z0-9._\-]+|xox[baprs]-[A-Za-z0-9-]{10,})", re.IGNORECASE),
        "password": re.compile(r"(?:password\s*[:=]\s*[^\s,;]+|passphrase\s*[:=]\s*[^\s,;]+)", re.IGNORECASE),
        "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
        "secret": re.compile(r"(?:secret\s*[:=]\s*[^\s,;]+|api_key\s*[:=]\s*[^\s,;]+)", re.IGNORECASE),
    }

    @staticmethod
    def scan(text: str) -> list[dict[str, str]]:
        findings: list[dict[str, str]] = []
        for kind, pattern in LeakageDetector.PATTERNS.items():
            for match in pattern.finditer(text):
                findings.append({"type": kind, "value": match.group(0), "span": match.span()})
        return findings

    @staticmethod
    def redact(text: str) -> tuple[str, list[dict[str, str]]]:
        findings = LeakageDetector.scan(text)
        redacted = text
        for finding in reversed(findings):
            redacted = redacted[: finding["span"][0]] + "[REDACTED]" + redacted[finding["span"][1] :]
        return redacted, findings

    @staticmethod
    def has_leakage(text: str) -> bool:
        return bool(LeakageDetector.scan(text))
