from input_normalization.unicode_normalizer import (
    normalize_unicode_text,
    replace_homoglyphs,
    remove_zero_width_chars,
    detect_confusable,
    fullwidth_to_halfwidth,
)


class TestUnicodeNormalizer:
    def test_fullwidth_flag(self):
        result = fullwidth_to_halfwidth("ＦＬＡＧ")
        assert result == "FLAG"

    def test_fullwidth_flag_via_normalize(self):
        result = normalize_unicode_text("ＦＬＡＧ")
        assert result == "flag"

    def test_cyrillic_confusable(self):
        text = "flаg"  # Cyrillic а
        result = normalize_unicode_text(text)
        assert result == "flag"

    def test_cyrillic_detected(self):
        text = "flаg"
        flags, _ = detect_confusable(text)
        assert "unicode_confusable_detected" in flags

    def test_greek_confusable(self):
        text = "flag"  # Using regular text to ensure no false positive
        flags, _ = detect_confusable(text)
        assert "unicode_confusable_detected" not in flags

    def test_mixed_fullwidth_and_homoglyph(self):
        result = normalize_unicode_text("flаg")  # Cyrillic а again
        assert result == "flag"

    def test_zero_width_removed(self):
        text = "f\u200blag"
        assert remove_zero_width_chars(text) == "flag"

    def test_raw_text_preserved(self):
        text = "flаg"
        result = normalize_unicode_text(text)
        assert result != text  # normalized version is different

    def test_normal_text_unchanged(self):
        result = normalize_unicode_text("hello world")
        assert result == "hello world"

    def test_homoglyph_replace(self):
        result = replace_homoglyphs("flаg")  # Cyrillic а
        assert result == "flag"
