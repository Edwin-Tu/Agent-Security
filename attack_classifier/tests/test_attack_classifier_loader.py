import sys
import json
import tempfile
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import pytest
from attack_classifier.pattern_loader import PatternLoader, PatternLoaderError


class TestPatternLoaderErrors:
    def test_load_attacks_file_not_found_raises_error(self):
        with pytest.raises(PatternLoaderError, match="not found"):
            PatternLoader.load_attacks("/tmp/nonexistent_attacks.json")

    def test_load_patterns_file_not_found_raises_error(self):
        with pytest.raises(PatternLoaderError, match="not found"):
            PatternLoader.load_attack_patterns("/tmp/nonexistent_patterns.json")

    def test_invalid_json_raises_loader_error(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("this is not json")
            f.flush()
            path = f.name
        try:
            with pytest.raises(PatternLoaderError, match="Invalid JSON"):
                PatternLoader.load_attacks(path)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_attacks_json_must_be_array(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"category": "test"}, f)
            f.flush()
            path = f.name
        try:
            with pytest.raises(PatternLoaderError, match="must contain a JSON array"):
                PatternLoader.load_attacks(path)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_patterns_json_must_be_array(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"rule_id": "test"}, f)
            f.flush()
            path = f.name
        try:
            with pytest.raises(PatternLoaderError, match="must contain a JSON array"):
                PatternLoader.load_attack_patterns(path)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_load_attacks_success(self):
        attacks_path = Path(__file__).resolve().parent.parent / "rules" / "attacks.json"
        data = PatternLoader.load_attacks(str(attacks_path))
        assert isinstance(data, list)
        assert len(data) > 0

    def test_load_patterns_success(self):
        patterns_path = Path(__file__).resolve().parent.parent / "rules" / "attack_patterns.json"
        data = PatternLoader.load_attack_patterns(str(patterns_path))
        assert isinstance(data, list)
        assert len(data) > 0

    def test_build_attack_map(self):
        attacks = [
            {"category": "test_cat", "name": "Test", "base_confidence": 0.5},
            {"category": "test_cat2", "name": "Test2"},
        ]
        mapping = PatternLoader.build_attack_map(attacks)
        assert "test_cat" in mapping
        assert mapping["test_cat"]["base_confidence"] == 0.5
        assert "test_cat2" in mapping
