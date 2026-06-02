import sys
import json
import pytest
import tempfile
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from asset_registry.asset_loader import AssetLoader


class TestAssetLoader:
    def test_load_from_json_valid(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"assets": [{"asset_id": "a", "value": "v"}]}, f)
            f.flush()
            assets = AssetLoader.load_from_json(Path(f.name))
            assert len(assets) == 1
            assert assets[0]["asset_id"] == "a"

    def test_load_from_json_missing_file(self):
        assets = AssetLoader.load_from_json(Path("/nonexistent/file.json"))
        assert assets == []

    def test_load_from_json_not_dict(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json")
            f.flush()
            with pytest.raises(json.JSONDecodeError):
                AssetLoader.load_from_json(Path(f.name))

    def test_load_from_directory(self):
        with tempfile.TemporaryDirectory() as d:
            p1 = Path(d) / "a.json"
            p2 = Path(d) / "b.json"
            with open(p1, "w") as f:
                json.dump({"assets": [{"asset_id": "a1", "value": "v1"}]}, f)
            with open(p2, "w") as f:
                json.dump({"assets": [{"asset_id": "b1", "value": "v2"}]}, f)
            assets = AssetLoader.load_from_directory(Path(d))
            assert len(assets) == 2

    def test_load_from_directory_empty(self):
        with tempfile.TemporaryDirectory() as d:
            assets = AssetLoader.load_from_directory(Path(d))
            assert assets == []

    def test_load_from_directory_not_exists(self):
        assets = AssetLoader.load_from_directory(Path("/nonexistent/dir"))
        assert assets == []
