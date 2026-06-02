from __future__ import annotations

from .case_normalizer import normalize_case
from .encoding_probe import probe_encoded_candidates
from .language_hint_detector import detect_aliases
from .normalization_result import NormalizationResult
from .punctuation_normalizer import detect_symbol_obfuscation, strip_symbols_and_compact
from .reconstruction_normalizer import detect_reconstruction_patterns
from .unicode_normalizer import detect_confusable, normalize_unicode_text, remove_zero_width_chars
from .whitespace_normalizer import compact_text, detect_spacing_obfuscation, normalize_whitespace


def normalize_input(raw_text: str) -> NormalizationResult:
    if not isinstance(raw_text, str):
        raw_text = str(raw_text)

    normalized_whitespace = normalize_whitespace(raw_text)
    normalized_text = normalize_unicode_text(normalized_whitespace)
    casefold_text = normalize_case(normalized_text)
    compact = compact_text(normalized_text)
    symbol_stripped_text = strip_symbols_and_compact(normalized_text)
    decoded_candidates, encoding_flags = probe_encoded_candidates(raw_text)
    matched_aliases, detected_languages = detect_aliases(normalized_text)
    reconstruction_detected, reconstruction_transformations = detect_reconstruction_patterns(raw_text)
    confusable_flags, confusable_transformations = detect_confusable(raw_text)

    flags = set()
    transformations = []

    if "unicode_confusable_detected" in confusable_flags:
        flags.add("unicode_confusable_detected")
        transformations.extend(confusable_transformations)

    if remove_zero_width_chars(raw_text) != raw_text:
        flags.add("zero_width_character_removed")
        transformations.append(
            {
                "type": "zero_width_character_removed",
                "from": raw_text,
                "to": remove_zero_width_chars(raw_text),
            }
        )

    if detect_spacing_obfuscation(raw_text):
        flags.add("spacing_obfuscation_detected")
        transformations.append(
            {
                "type": "spacing_obfuscation_detected",
                "text": raw_text,
            }
        )

    if detect_symbol_obfuscation(normalized_text, symbol_stripped_text):
        flags.add("symbol_obfuscation_detected")
        transformations.append(
            {
                "type": "symbol_obfuscation_detected",
                "from": normalized_text,
                "to": symbol_stripped_text,
            }
        )

    flags.update(encoding_flags)

    if matched_aliases:
        flags.add("cross_language_alias_detected")

    if reconstruction_detected:
        flags.add("reconstruction_pattern_detected")
        transformations.extend(reconstruction_transformations)

    suspicion_flags = sorted(flags)

    return NormalizationResult(
        raw_text=raw_text,
        normalized_text=normalized_text,
        casefold_text=casefold_text,
        compact_text=compact,
        symbol_stripped_text=symbol_stripped_text,
        decoded_candidates=decoded_candidates,
        detected_languages=detected_languages,
        matched_aliases=matched_aliases,
        suspicion_flags=suspicion_flags,
        transformations=transformations,
    )
