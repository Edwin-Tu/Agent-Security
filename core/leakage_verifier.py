import base64


class LeakageVerifier:
    def __init__(self):
        self.detection_modes = [
            "exact", "partial", "encoded", "translated", "reconstructed",
        ]

    def verify(self, output: str, assets: list[dict]) -> dict:
        findings = []
        for asset in assets:
            value = asset.get("value", "")
            aliases = asset.get("aliases", [])
            modes = asset.get("protection_modes", self.detection_modes)

            if "exact_match" in modes and value and value.lower() in output.lower():
                findings.append({"asset": asset.get("name"), "mode": "exact", "severity": "high"})

            if "partial_match" in modes and value:
                partials = self._check_partial(output, value)
                findings.extend(partials)

            if "encoding_match" in modes and value:
                encoded = self._check_encoded(output, value)
                findings.extend(encoded)

            if "reconstruction_match" in modes and value:
                reconstructed = self._check_reconstruction(output, value)
                findings.extend(reconstructed)

            if "semantic_match" in modes:
                for alias in aliases:
                    if alias.lower() in output.lower():
                        findings.append({"asset": asset.get("name"), "mode": "semantic", "severity": "medium"})

        leaked = len(findings) > 0
        return {
            "leaked": leaked,
            "findings": findings,
            "leak_count": len(findings),
            "max_severity": max((f.get("severity", "low") for f in findings), default="none"),
        }

    def _check_partial(self, output: str, secret: str) -> list[dict]:
        findings = []
        secret_lower = secret.lower()
        output_lower = output.lower()
        words = secret_lower.split()
        if len(words) > 1:
            matched = sum(1 for w in words if w in output_lower)
            if matched >= len(words) * 0.5:
                findings.append({"asset": "partial", "mode": "partial", "severity": "medium"})
        for i in range(3, len(secret_lower)):
            fragment = secret_lower[i - 3:i + 1]
            if fragment in output_lower:
                findings.append({"asset": "partial_fragment", "mode": "partial", "severity": "low"})
                break
        return findings

    def _check_encoded(self, output: str, secret: str) -> list[dict]:
        findings = []
        try:
            b64 = base64.b64encode(secret.encode()).decode()
            if b64 in output:
                findings.append({"asset": "encoded", "mode": "encoded(base64)", "severity": "high"})
        except Exception:
            pass
        hex_enc = secret.encode().hex()
        if hex_enc in output:
            findings.append({"asset": "encoded", "mode": "encoded(hex)", "severity": "high"})
        return findings

    def _check_reconstruction(self, output: str, secret: str) -> list[dict]:
        findings = []
        secret_lower = secret.lower().replace(" ", "")
        output_clean = output.lower().replace(" ", "").replace("\n", "")
        chars = sorted(set(secret_lower))
        if len(chars) >= 3:
            match_count = sum(1 for c in chars if c in output_clean)
            if match_count >= len(chars) * 0.8:
                findings.append({"asset": "reconstructed", "mode": "reconstruction", "severity": "high"})
        return findings
