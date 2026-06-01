from dataclasses import dataclass, field


@dataclass
class NormalizationResult:
    raw_text: str
    normalized_text: str
    casefold_text: str
    compact_text: str
    symbol_stripped_text: str
    decoded_candidates: list[str] = field(default_factory=list)
    detected_languages: list[str] = field(default_factory=list)
    matched_aliases: list[str] = field(default_factory=list)
    suspicion_flags: list[str] = field(default_factory=list)
    transformations: list[dict] = field(default_factory=list)
