class AssetRedactor:
    def redact(self, asset: dict) -> dict:
        return {
            "asset_ref": asset.get("asset_id", ""),
            "type": asset.get("type", ""),
            "risk_level": asset.get("risk_level", ""),
            "protection_modes": asset.get("protection_modes", []),
        }

    def redact_all(self, assets: list[dict]) -> list[dict]:
        return [self.redact(a) for a in assets]
