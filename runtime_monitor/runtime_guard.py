from __future__ import annotations
from typing import Iterable

from .stream_monitor import RuntimeStreamMonitor
from .interruption_handler import InterruptionHandler


class RuntimeGuard:
    def __init__(self, monitor: RuntimeStreamMonitor, handler: InterruptionHandler):
        self._monitor = monitor
        self._handler = handler

    def process_stream(self, chunks: Iterable[str]) -> str:
        output_parts: list[str] = []
        for chunk in chunks:
            result = self._monitor.inspect_chunk(chunk)
            if result.interrupted:
                safe = self._handler.build_safe_response(result)
                return safe or "此回應可能包含受保護資訊，已中止生成。"
            output_parts.append(chunk)
        return "".join(output_parts)

    def check_output(self, text: str) -> dict:
        result = self._monitor.inspect_chunk(text)
        if result.interrupted:
            self._handler.interrupt(result.reason, "output_check")
            return {"blocked": True, "reason": result.reason, "matched_tokens": [result.matched_type] if result.matched_type else []}
        return {"blocked": False, "reason": "Output passed."}

    def check_stream(self, chunks: Iterable[str]) -> str:
        return self.process_stream(chunks)

    def reset(self):
        self._monitor.reset()
        self._handler.clear()
