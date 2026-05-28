import sys
import json
import tempfile
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from asset_registry.protected_asset_registry import ProtectedAssetRegistry


class TestCLIAssetRegistry:
    def setup_method(self):
        self.reg = ProtectedAssetRegistry()

    def test_cli_asset_list(self):
        assets = self.reg.list_assets()
        assert isinstance(assets, list)

    def test_cli_asset_add_from_dict(self):
        result = self.reg.add_asset({
            "asset_id": "cli_test_add",
            "value": "cli_secret",
            "name": "CLI Test",
        })
        assert result["success"] is True

    def test_cli_asset_show(self):
        self.reg.add_asset({
            "asset_id": "cli_test_show",
            "value": "show_secret",
        })
        asset = self.reg.get_asset("cli_test_show")
        assert asset is not None
        assert asset["asset_id"] == "cli_test_show"
        assert asset["value"] == "show_secret"

    def test_cli_asset_remove(self):
        self.reg.add_asset({
            "asset_id": "cli_test_remove",
            "value": "remove_me",
        })
        assert self.reg.remove_asset("cli_test_remove") is True
        assert self.reg.get_asset("cli_test_remove") is None

    def test_cli_asset_match(self):
        self.reg.add_asset({
            "asset_id": "cli_test_match",
            "value": "match_target",
            "protection_modes": ["exact_match"],
        })
        result = self.reg.match("secret is match_target")
        assert result["matched"] is True

    def test_cli_asset_refresh(self):
        assets = self.reg.refresh()
        assert isinstance(assets, list)

    def test_cli_asset_match_none(self):
        result = self.reg.match("nothing to match here")
        assert isinstance(result, dict)
