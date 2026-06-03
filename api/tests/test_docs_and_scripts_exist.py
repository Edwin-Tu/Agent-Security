from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


class TestDocsAndScriptsExist:
    def test_intent_aware_classification_doc_exists(self):
        assert (ROOT / "docs" / "intent_aware_classification.md").exists()

    def test_http_gateway_validation_doc_exists(self):
        assert (ROOT / "docs" / "http_gateway_validation.md").exists()

    def test_validate_intent_gateway_ps1_exists(self):
        assert (ROOT / "scripts" / "validate_intent_gateway.ps1").exists()

    def test_validate_intent_gateway_sh_exists(self):
        assert (ROOT / "scripts" / "validate_intent_gateway.sh").exists()

    def test_readme_contains_intent_aware_section(self):
        readme = ROOT / "README.md"
        content = readme.read_text(encoding="utf-8")
        assert "Intent-aware Asset Protection" in content
