from .leakage_result import LeakageResult, LeakageMatch
from .leakage_types import SEVERITY_ORDER, LEAK_SEVERITY_MAP, LEAK_ACTION_MAP, NO_LEAK
from . import leakage_types as lt
from .exact_leak_detector import ExactLeakDetector
from .partial_leak_detector import PartialLeakDetector
from .encoding_leak_detector import EncodingLeakDetector
from .reconstruction_leak_detector import ReconstructionLeakDetector
from .translation_leak_detector import TranslationLeakDetector
from .semantic_leak_detector import SemanticLeakDetector
from .redactor import Redactor


MODE_DETECTOR_MAP = {
    "exact_match": ExactLeakDetector,
    "partial_match": PartialLeakDetector,
    "encoding_match": EncodingLeakDetector,
    "reconstruction_match": ReconstructionLeakDetector,
    "translation_match": TranslationLeakDetector,
    "semantic_match": SemanticLeakDetector,
}


class LeakageVerifier:
    def __init__(self):
        self.redactor = Redactor()

    def verify(
        self,
        output_text: str,
        protected_assets: list[dict],
        policy_context: dict | None = None,
        session_context: dict | None = None,
    ) -> LeakageResult:
        all_matches: list[LeakageMatch] = []

        for asset in protected_assets:
            modes = asset.get("protection_modes", list(MODE_DETECTOR_MAP.keys()))
            for mode in modes:
                detector_cls = MODE_DETECTOR_MAP.get(mode)
                if detector_cls is None:
                    continue
                detector = detector_cls()
                try:
                    matches = detector.detect(output_text, asset, session_context)
                    all_matches.extend(matches)
                except Exception:
                    continue

        if not all_matches:
            return LeakageResult(
                is_leak=False,
                highest_severity=lt.SEVERITY_NONE,
                leak_types=[],
                matches=[],
                recommended_action=LEAK_ACTION_MAP[NO_LEAK],
                redacted_output=output_text,
            )

        leak_types = list(set(m.leak_type for m in all_matches))
        highest_severity = max(
            (m.severity for m in all_matches),
            key=lambda s: SEVERITY_ORDER.get(s, 0),
        )

        if lt.SEVERITY_CRITICAL in [m.severity for m in all_matches]:
            recommended_action = "block"
        elif lt.SEVERITY_HIGH in [m.severity for m in all_matches]:
            recommended_action = "block"
        else:
            recommended_action = "redact"

        redacted = output_text
        for match in sorted(all_matches, key=lambda m: m.leak_type != lt.FULL_LEAK):
            text_to_redact = match.matched_text or (match.matched_fragments[0] if match.matched_fragments else None)
            if text_to_redact:
                redacted = self.redactor.redact(redacted, text_to_redact, match.leak_type)

        return LeakageResult(
            is_leak=True,
            highest_severity=highest_severity,
            leak_types=leak_types,
            matches=all_matches,
            recommended_action=recommended_action,
            redacted_output=redacted,
        )
