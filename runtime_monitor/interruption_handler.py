from __future__ import annotations
from typing import Optional

from .monitor_result import RuntimeMonitorResult


class InterruptionHandler:
    def __init__(self):
        self.interrupted: bool = False
        self.reason: str = ""
        self.stage: str = ""

    def interrupt(self, reason: str = "", stage: str = ""):
        self.interrupted = True
        self.reason = reason
        self.stage = stage

    def clear(self):
        self.interrupted = False
        self.reason = ""
        self.stage = ""

    def is_interrupted(self) -> bool:
        return self.interrupted

    def get_reason(self) -> str:
        return self.reason

    def build_safe_response(self, result: RuntimeMonitorResult) -> Optional[str]:
        if result.allowed is True or result.interrupted is False:
            return None

        return (
            "此回應可能包含受保護資訊，已中止生成。\n"
            "我可以協助回答不涉及敏感內容的部分。"
        )
