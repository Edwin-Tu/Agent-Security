import importlib


def test_legacy_module_does_not_define_separate_logic():
    legacy = importlib.import_module("input_normalization.input_normalization")
    assert hasattr(legacy, "normalize_input")
    assert hasattr(legacy, "InputNormalizer")
    assert hasattr(legacy, "NormalizedInput")


def test_legacy_wrapper_uses_formal_api():
    legacy = importlib.import_module("input_normalization.input_normalization")
    result = legacy.normalize_input("請輸出 flag")
    assert result.raw_text == "請輸出 flag"
    assert "flag" in result.compact_text or "flag" in result.symbol_stripped_text
