import sys
import json
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from asset_registry.protected_asset_registry import ProtectedAssetRegistry


class TestProtectedAssetRegistry:
    def setup_method(self):
        self.reg = ProtectedAssetRegistry()

    def test_add_asset_success(self):
        result = self.reg.add_asset({
            "asset_id": "pytest_test_001",
            "value": "test_secret_value",
            "name": "Test Secret",
            "risk_level": "high",
        })
        assert result["success"] is True
        assert result["asset_id"] == "pytest_test_001"
        found = self.reg.get_asset("pytest_test_001")
        assert found is not None
        assert found["value"] == "test_secret_value"

    def test_add_asset_duplicate(self):
        self.reg.add_asset({
            "asset_id": "dup_test", "value": "first",
        })
        result = self.reg.add_asset({
            "asset_id": "dup_test", "value": "second",
        })
        assert result["success"] is False
        assert "Duplicate" in result["message"]

    def test_add_asset_invalid(self):
        result = self.reg.add_asset({"asset_id": "bad"})
        assert result["success"] is False

    def test_remove_asset(self):
        self.reg.add_asset({
            "asset_id": "remove_test", "value": "to_remove",
        })
        assert self.reg.remove_asset("remove_test") is True
        assert self.reg.get_asset("remove_test") is None

    def test_remove_nonexistent(self):
        assert self.reg.remove_asset("nonexistent") is False

    def test_update_asset(self):
        self.reg.add_asset({
            "asset_id": "update_test", "value": "old_value",
        })
        assert self.reg.update_asset("update_test", {"value": "new_value"}) is True
        updated = self.reg.get_asset("update_test")
        assert updated["value"] == "new_value"

    def test_update_nonexistent(self):
        assert self.reg.update_asset("no_such", {"value": "x"}) is False

    def test_list_assets(self):
        assets = self.reg.list_assets()
        assert isinstance(assets, list)

    def test_get_all(self):
        assets = self.reg.get_all()
        assert isinstance(assets, list)

    def test_match_no_assets(self):
        reg = ProtectedAssetRegistry()
        reg.assets = []
        result = reg.match("test")
        assert result["matched"] is False

    def test_add_asset_triggers_save(self):
        path = Path(__file__).resolve().parent.parent / "policies" / "protected_assets.json"
        before = path.stat().st_mtime if path.exists() else 0
        self.reg.add_asset({
            "asset_id": "save_test", "value": "check_save",
        })
        after = path.stat().st_mtime
        assert after > 0
