from input_normalization.punctuation_normalizer import (
    strip_symbols_and_compact,
    detect_symbol_obfuscation,
)


class TestPunctuationNormalizer:
    def test_dash_separated(self):
        result = strip_symbols_and_compact("f-l-a-g")
        assert result == "flag"

    def test_underscore_separated(self):
        result = strip_symbols_and_compact("f_l_a_g")
        assert result == "flag"

    def test_dot_separated(self):
        result = strip_symbols_and_compact("f.l.a.g")
        assert result == "flag"

    def test_slash_separated(self):
        result = strip_symbols_and_compact("f/l/a/g")
        assert result == "flag"

    def test_asterisk_separated(self):
        result = strip_symbols_and_compact("s*y*s*t*e*m p*r*o*m*p*t")
        assert result == "system prompt"

    def test_symbol_obfuscation_detected(self):
        assert detect_symbol_obfuscation("f-l-a-g", "flag") is True

    def test_no_symbol_obfuscation(self):
        assert detect_symbol_obfuscation("flag", "flag") is False

    def test_normal_text_unchanged(self):
        result = strip_symbols_and_compact("hello world")
        assert result == "hello world"

    def test_mixed_language_with_symbols(self):
        result = strip_symbols_and_compact("通-關-碼")
        assert result == "通關碼"
