from input_normalization.case_normalizer import normalize_case


class TestCaseNormalizer:
    def test_flag_upper(self):
        assert normalize_case("FLAG") == "flag"

    def test_flag_capitalized(self):
        assert normalize_case("Flag") == "flag"

    def test_flag_mixed(self):
        assert normalize_case("fLaG") == "flag"

    def test_system_prompt_upper(self):
        assert normalize_case("SYSTEM PROMPT") == "system prompt"

    def test_unchanged_lowercase(self):
        assert normalize_case("flag") == "flag"

    def test_mixed_case_with_spaces(self):
        assert normalize_case("My SecRET Flag") == "my secret flag"

    def test_unicode_casefold(self):
        result = normalize_case("STRASSE")
        assert "strasse" in result or result == "strasse"
