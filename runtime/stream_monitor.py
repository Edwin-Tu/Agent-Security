"""
stream_monitor.py
=================
監控模型的 streaming output。
逐段接收 chunk，即時檢查 buffer 是否命中限制 token，
若命中則中斷輸出並回傳安全拒答。
"""

import sys
from pathlib import Path
from typing import Iterable, Optional

# 將專案根目錄加入 sys.path，讓直接執行時能找到 guards 等模組
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from guards.restricted_token_guard import RestrictedTokenGuard


class StreamMonitor:
    """
    串流監控器。

    使用方式：
        guard = RestrictedTokenGuard(restricted_tokens=["password"])
        monitor = StreamMonitor(guard)
        result = monitor.monitor(["The ", "password ", "is ", "123456."])
    """

    def __init__(
        self,
        guard: RestrictedTokenGuard,
        max_buffer_size: int = 1000,
    ):
        """
        初始化串流監控器。

        參數
        -----
        guard : RestrictedTokenGuard
            限制 token 防護器實例。
        max_buffer_size : int
            buffer 最大字元數，超過時只保留最後 N 個字元。
        """
        self.guard = guard
        self.max_buffer_size = max_buffer_size

    def monitor(self, stream_chunks: Iterable[Optional[str]]) -> dict:
        """
        監控串流輸出，逐段檢查是否命中限制 token。

        參數
        -----
        stream_chunks : Iterable[str | None]
            模型串流輸出的 chunk 序列。

        回傳
        -----
        dict
            {
                "blocked": bool,
                "output": str,
                "matched_tokens": list[str],
                "reason": str,
            }
        """
        buffer = ""         # 累積接收到的文字
        output = ""         # 實際累積的輸出（未受阻擋的內容）
        blocked = False
        matched_tokens: list[str] = []

        for chunk in stream_chunks:
            # 跳過 None
            if chunk is None:
                continue

            # 確保 chunk 是字串
            if not isinstance(chunk, str):
                chunk = str(chunk)

            # 更新 buffer
            buffer += chunk

            # 限制 buffer 大小，避免無限膨脹
            if len(buffer) > self.max_buffer_size:
                buffer = buffer[-self.max_buffer_size:]

            # 檢查 buffer 是否命中限制詞
            result = self.guard.detect_in_stream(buffer)

            if result["blocked"]:
                blocked = True
                matched_tokens = result["matched_tokens"]
                # 命中限制詞，中斷串流
                break

            # 未命中，累積輸出
            output += chunk

        # 根據 blocked 狀態回傳結果
        if blocked:
            return {
                "blocked": True,
                "output": "[SecretGuard]\n此內容受到限制，未經授權無法提供。",
                "matched_tokens": matched_tokens,
                "reason": "Restricted token detected during streaming.",
            }

        return {
            "blocked": False,
            "output": output,
            "matched_tokens": [],
            "reason": "Stream completed without restricted token.",
        }


# =====================================================
# 簡易測試
# =====================================================
if __name__ == "__main__":
    from guards.restricted_token_guard import RestrictedTokenGuard

    print("=" * 50)
    print("StreamMonitor Test")
    print("=" * 50)

    # 建立防護器，限制 token 為 "password"
    guard = RestrictedTokenGuard(restricted_tokens=["password"])

    # 建立串流監控器
    monitor = StreamMonitor(guard)

    # 模擬串流 chunk
    stream_chunks = ["The ", "password ", "is ", "123456."]
    print(f"stream_chunks: {stream_chunks}")

    result = monitor.monitor(stream_chunks)
    print(f"\nmonitor result:")
    print(f"  blocked:        {result['blocked']}")
    print(f"  matched_tokens: {result['matched_tokens']}")
    print(f"  reason:         {result['reason']}")
    print(f"  output:\n{result['output']}")
