from prompt_builder.refusal_builder import RefusalBuilder


def test_refusal_no_secret_value():
    builder = RefusalBuilder()
    result = builder.build()
    assert "picoCTF" not in result
    assert "sk-" not in result


def test_refusal_contains_refusal_semantics():
    builder = RefusalBuilder()
    result = builder.build()
    assert "不能提供" in result or "無法提供" in result or "cannot provide" in result


def test_refusal_contains_safe_alternative():
    builder = RefusalBuilder()
    result = builder.build()
    assert "協助" in result or "了解" in result or "help" in result or "assist" in result


def test_refusal_is_non_empty_string():
    builder = RefusalBuilder()
    result = builder.build()
    assert isinstance(result, str)
    assert len(result) > 0


def test_refusal_no_asset_specific_content():
    builder = RefusalBuilder()
    result = builder.build()
    assert "secret_001" not in result
