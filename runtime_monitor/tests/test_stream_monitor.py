import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from prompt_builder.restricted_token_guard import RestrictedTokenGuard
from runtime_monitor.stream_monitor import StreamMonitor


def test_stream_monitor_blocks_cross_chunk_secret():
    guard = RestrictedTokenGuard(restricted_tokens=["password"])
    monitor = StreamMonitor(guard)

    chunks = ["the pa", "ss", "word is 123"]
    result = monitor.monitor(chunks)

    assert result["blocked"] is True
    assert "password" in [t.lower() for t in result["matched_tokens"]]


def test_stream_monitor_passes_safe_stream():
    guard = RestrictedTokenGuard(restricted_tokens=["password"])
    monitor = StreamMonitor(guard)

    chunks = ["today weather ", "is sunny"]
    result = monitor.monitor(chunks)

    assert result["blocked"] is False
    assert result["matched_tokens"] == []
