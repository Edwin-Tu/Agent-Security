from input_normalization.whitespace_normalizer import (
    normalize_whitespace,
    compact_text,
    detect_spacing_obfuscation,
)


class TestWhitespaceNormalizer:
    def test_multiple_spaces(self):
        assert normalize_whitespace("hello    world") == "hello world"

    def test_tab_to_space(self):
        assert normalize_whitespace("hello\tworld") == "hello world"

    def test_newline_to_space(self):
        assert normalize_whitespace("hello\nworld") == "hello world"

    def test_windows_newline(self):
        assert normalize_whitespace("hello\r\nworld") == "hello world"

    def test_fullwidth_space(self):
        assert normalize_whitespace("hello\u3000world") == "hello world"

    def test_zero_width_chars_removed(self):
        result = normalize_whitespace("he\u200bl\u200clo")
        assert result == "hello"

    def test_compact_f_l_a_g(self):
        assert compact_text("f l a g") == "flag"

    def test_compact_with_tabs(self):
        assert compact_text("f\tl\ta\tg") == "flag"

    def test_compact_chinese(self):
        assert compact_text("請 輸 出") == "請輸出"

    def test_detect_spacing_obfuscation_true(self):
        assert detect_spacing_obfuscation("f l a g") is True

    def test_detect_spacing_obfuscation_false(self):
        assert detect_spacing_obfuscation("hello world") is False

    def test_empty_string(self):
        assert normalize_whitespace("") == ""
        assert compact_text("") == ""

    def test_leading_trailing_spaces(self):
        assert normalize_whitespace("  hello  ") == "hello"
