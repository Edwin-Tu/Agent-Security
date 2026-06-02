from runtime_monitor.stream_monitor import StreamMonitor, StreamCheckResult

DEFAULT_PATTERNS = ["api_key", "sk-", "picoCTF{", "BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY"]


def test_clean_chunk_allowed():
    monitor = StreamMonitor(DEFAULT_PATTERNS)
    result = monitor.inspect_chunk("Hello world")
    assert result.allowed is True
    assert result.reason is None


def test_single_chunk_matches_api_key():
    monitor = StreamMonitor(DEFAULT_PATTERNS)
    result = monitor.inspect_chunk("my api_key is secret")
    assert result.allowed is False
    assert result.matched_pattern == "api_key"


def test_single_chunk_matches_sk_prefix():
    monitor = StreamMonitor(DEFAULT_PATTERNS)
    result = monitor.inspect_chunk("token is sk-abc123")
    assert result.allowed is False
    assert result.matched_pattern == "sk-"


def test_single_chunk_matches_picoctf():
    monitor = StreamMonitor(DEFAULT_PATTERNS)
    result = monitor.inspect_chunk("flag: picoCTF{secret_flag}")
    assert result.allowed is False
    assert "picoctf{" in result.matched_pattern.lower()


def test_single_chunk_matches_private_key():
    monitor = StreamMonitor(DEFAULT_PATTERNS)
    result = monitor.inspect_chunk("-----BEGIN PRIVATE KEY-----")
    assert result.allowed is False
    assert "private key" in result.matched_pattern.lower()


def test_cross_chunk_detection():
    monitor = StreamMonitor(DEFAULT_PATTERNS)
    r1 = monitor.inspect_chunk("my api_ke")
    assert r1.allowed is True
    r2 = monitor.inspect_chunk("y is 12345")
    assert r2.allowed is False
    assert r2.matched_pattern == "api_key"


def test_cross_chunk_sk_detection():
    monitor = StreamMonitor(DEFAULT_PATTERNS)
    r1 = monitor.inspect_chunk("token: s")
    assert r1.allowed is True
    r2 = monitor.inspect_chunk("k-abc")
    assert r2.allowed is False
    assert r2.matched_pattern == "sk-"


def test_blocked_stops_further_output():
    monitor = StreamMonitor(DEFAULT_PATTERNS)
    r1 = monitor.inspect_chunk("hello ")
    assert r1.allowed is True
    r2 = monitor.inspect_chunk("api_key here")
    assert r2.allowed is False
    r3 = monitor.inspect_chunk("more text")
    assert r3.allowed is False


def test_done_event_after_clean_stream():
    monitor = StreamMonitor(DEFAULT_PATTERNS)
    assert monitor.interrupted is False
    monitor.inspect_chunk("safe text")
    assert monitor.interrupted is False
    monitor.inspect_chunk("more safe")
    assert monitor.interrupted is False


def test_inspect_chunk_returns_stream_check_result():
    monitor = StreamMonitor(DEFAULT_PATTERNS)
    result = monitor.inspect_chunk("safe")
    assert isinstance(result, StreamCheckResult)
    assert hasattr(result, "allowed")
    assert hasattr(result, "reason")
    assert hasattr(result, "risk_score")
    assert hasattr(result, "matched_pattern")


def test_case_insensitive_matching():
    monitor = StreamMonitor(DEFAULT_PATTERNS)
    r1 = monitor.inspect_chunk("API_KEY is here")
    assert r1.allowed is False
    assert r1.matched_pattern == "api_key"
    monitor2 = StreamMonitor(DEFAULT_PATTERNS)
    r2 = monitor2.inspect_chunk("Sk-123")
    assert r2.allowed is False
