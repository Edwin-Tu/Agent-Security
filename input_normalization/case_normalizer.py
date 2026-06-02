def normalize_case(text: str) -> str:
    """Use Unicode-aware case folding for normalization."""
    if not isinstance(text, str):
        text = str(text)
    return text.casefold()
