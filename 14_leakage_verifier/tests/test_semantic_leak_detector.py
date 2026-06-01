import pytest
from leakage_verifier.semantic_leak_detector import SemanticLeakDetector


class TestSemanticLeakDetector:

    @pytest.fixture
    def detector(self):
        return SemanticLeakDetector()

    def test_detects_semantic_alias_leak(self, detector):
        asset = {
            "asset_id": "secret_001",
            "name": "裁員計畫",
            "type": "semantic_secret",
            "value": "公司下月將進行未公開人力縮編",
            "aliases": ["裁員", "人力縮編", "未公開組織調整"],
        }
        result = detector.detect("公司下個月可能有人力縮編安排。", asset)
        assert len(result) == 1
        assert result[0].leak_type == "semantic_leak"

    def test_single_common_word_is_not_high_risk(self, detector):
        asset = {
            "asset_id": "secret_001",
            "name": "裁員計畫",
            "type": "semantic_secret",
            "value": "公司下月將進行未公開人力縮編",
            "aliases": ["裁員", "人力縮編", "未公開組織調整"],
        }
        result = detector.detect("公司今天有下午茶。", asset)
        assert len(result) == 0

    def test_multiple_sensitive_terms_raise_severity(self, detector):
        asset = {
            "asset_id": "secret_001",
            "name": "裁員計畫",
            "type": "semantic_secret",
            "value": "公司下月將進行未公開人力縮編",
            "aliases": ["裁員", "人力縮編", "未公開組織調整"],
        }
        result = detector.detect("公司正在討論裁員和人力縮編的未公開組織調整方案。", asset)
        assert len(result) == 1
        assert result[0].severity in ("high", "critical")
