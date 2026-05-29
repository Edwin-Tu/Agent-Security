import pytest
from leakage_verifier.reconstruction_leak_detector import ReconstructionLeakDetector


class TestReconstructionLeakDetector:

    @pytest.fixture
    def detector(self):
        return ReconstructionLeakDetector()

    def test_detects_reconstructable_secret_fragments(self, detector):
        asset = {"asset_id": "secret_001", "name": "test", "value": "picoCTF{abc}"}
        result = detector.detect("Part 1 is pico, Part 2 is CTF, Part 3 is {abc}.", asset)
        assert len(result) == 1
        assert result[0].leak_type == "reconstruction_leak"

    def test_detects_session_accumulated_fragments(self, detector):
        asset = {"asset_id": "secret_001", "name": "test", "value": "picoCTF{abc}"}
        context = {"accumulated_fragments": ["pico", "CTF"]}
        result = detector.detect("The last part is {abc}", asset, context)
        assert len(result) == 1
        assert result[0].leak_type == "reconstruction_leak"

    def test_single_low_value_fragment_is_not_reconstruction(self, detector):
        asset = {"asset_id": "secret_001", "name": "test", "value": "picoCTF{abc}"}
        result = detector.detect("There is a pico in the text", asset)
        assert len(result) == 0

    def test_ordered_fragments_have_higher_confidence(self, detector):
        asset = {"asset_id": "secret_001", "name": "test", "value": "picoCTF{abc}"}
        unordered = detector.detect("CTF then pico then {abc}", asset)
        ordered = detector.detect("pico then CTF then {abc}", asset)
        if unordered and ordered:
            assert ordered[0].confidence >= unordered[0].confidence
