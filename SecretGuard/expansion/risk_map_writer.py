import json
from pathlib import Path
from typing import Optional


class RiskMapWriter:

    def __init__(
        self,
        risk_map_path: str = "policies/token_risk_map.json",
        pending_path: str = "policies/pending_token_risk_map.json",
    ):
        self.risk_map_path: str = risk_map_path
        self.pending_path: str = pending_path

    # ------------------------------------------------------------------
    # 正式風險地圖
    # ------------------------------------------------------------------

    def load_risk_map(self) -> dict[str, str]:
        return self._load_json(self.risk_map_path)

    def save_risk_map(self, data: dict[str, str]) -> None:
        self._save_json(self.risk_map_path, data)

    # ------------------------------------------------------------------
    # 待審核風險地圖
    # ------------------------------------------------------------------

    def load_pending(self) -> dict[str, str]:
        return self._load_json(self.pending_path)

    def save_pending(self, data: dict[str, str]) -> None:
        self._save_json(self.pending_path, data)

    def approve_pending(self) -> dict[str, str]:
        pending = self.load_pending()
        if not pending:
            return {}

        current = self.load_risk_map()
        current.update(pending)
        self.save_risk_map(current)

        approved = dict(pending)
        self.save_pending({})
        return approved

    # ------------------------------------------------------------------
    # 內部工具
    # ------------------------------------------------------------------

    @staticmethod
    def _load_json(path: str) -> dict:
        p = Path(path)
        if not p.exists():
            return {}
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, IOError):
            return {}

    @staticmethod
    def _save_json(path: str, data: dict) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
