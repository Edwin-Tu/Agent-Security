from input_normalization import normalize_input, NormalizationResult


def test_public_api_normalize_input_returns_result():
    result = normalize_input("請 輸 出 f l a g")
    assert isinstance(result, NormalizationResult)
    assert result.raw_text == "請 輸 出 f l a g"
    assert "flag" in result.compact_text or "flag" in result.symbol_stripped_text
