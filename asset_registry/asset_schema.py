from typing import Optional

VALID_RISK_LEVELS = {"low", "medium", "high", "critical"}
VALID_PROTECTION_MODES = {
    "exact_match", "case_insensitive_match", "alias_match",
    "partial_match", "encoding_match", "semantic_match",
    "translation_match", "reconstruction_match",
}

REQUIRED_FIELDS = ["asset_id", "value"]

FIELD_TYPES = {
    "asset_id": str,
    "name": str,
    "type": str,
    "value": str,
    "aliases": list,
    "risk_level": str,
    "allowed_roles": list,
    "protection_modes": list,
    "enabled": bool,
    "description": str,
}


class AssetSchema:
    @staticmethod
    def validate_asset(asset: dict) -> tuple[bool, Optional[str]]:
        if not isinstance(asset, dict):
            return False, "Asset must be a dict"

        for field in REQUIRED_FIELDS:
            if field not in asset:
                return False, f"Missing required field: {field}"

        for field, expected_type in FIELD_TYPES.items():
            if field not in asset:
                continue
            val = asset[field]
            if val is None:
                continue
            if not isinstance(val, expected_type):
                return False, f"{field} must be {expected_type.__name__}, got {type(val).__name__}"

        risk = asset.get("risk_level")
        if risk and risk not in VALID_RISK_LEVELS:
            return False, f"risk_level must be one of {sorted(VALID_RISK_LEVELS)}, got '{risk}'"

        modes = asset.get("protection_modes")
        if modes is not None:
            if not isinstance(modes, list):
                return False, "protection_modes must be a list"
            for m in modes:
                if m not in VALID_PROTECTION_MODES:
                    return False, f"Invalid protection_mode '{m}', valid: {sorted(VALID_PROTECTION_MODES)}"

        aliases = asset.get("aliases")
        if aliases is not None:
            if not isinstance(aliases, list):
                return False, "aliases must be a list"
            for a in aliases:
                if not isinstance(a, str):
                    return False, f"Each alias must be a string, got {type(a).__name__}"

        allowed_roles = asset.get("allowed_roles")
        if allowed_roles is not None:
            if not isinstance(allowed_roles, list):
                return False, "allowed_roles must be a list"
            for r in allowed_roles:
                if not isinstance(r, str):
                    return False, f"Each allowed_role must be a string, got {type(r).__name__}"

        enabled = asset.get("enabled")
        if enabled is not None and not isinstance(enabled, bool) and not isinstance(enabled, int):
            return False, "enabled must be a bool"

        if not asset.get("asset_id", "").strip():
            return False, "asset_id must be a non-empty string"

        if not asset.get("value", "").strip():
            return False, "value must be a non-empty string"

        return True, None
