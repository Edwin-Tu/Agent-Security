from input_normalization.language_hint_detector import detect_aliases


class TestLanguageHintDetector:
    def test_detect_flag_alias_chinese(self):
        aliases, languages = detect_aliases("通關碼")
        assert "flag" in aliases
        assert "zh" in languages

    def test_detect_flag_alias_answer(self):
        aliases, languages = detect_aliases("答案")
        assert "flag" in aliases
        assert "zh" in languages

    def test_detect_password_alias(self):
        aliases, languages = detect_aliases("密碼")
        assert "password" in aliases
        assert "zh" in languages

    def test_detect_system_prompt_alias(self):
        aliases, languages = detect_aliases("系統提示詞")
        assert "system_prompt" in aliases
        assert "zh" in languages

    def test_detect_english_language_hint(self):
        aliases, languages = detect_aliases("please send the flag")
        assert "flag" in aliases or languages == ["en"]
