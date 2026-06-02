from prompt_builder.scope_builder import ScopeBuilder


def test_allowed_scope_generates_block():
    builder = ScopeBuilder()
    allowed = ["一般概念", "安全替代方案", "授權流程"]
    block = builder.build_allowed_scope(allowed)
    assert isinstance(block, str)
    for item in allowed:
        assert item in block


def test_denied_scope_generates_block():
    builder = ScopeBuilder()
    denied = ["secret value", "partial secret"]
    block = builder.build_denied_scope(denied)
    assert isinstance(block, str)
    for item in denied:
        assert item in block


def test_empty_allowed_scope_uses_default():
    builder = ScopeBuilder()
    block = builder.build_allowed_scope([])
    assert "一般概念" in block or "general" in block or "safe" in block


def test_empty_denied_scope_uses_default():
    builder = ScopeBuilder()
    block = builder.build_denied_scope([])
    assert "部分" in block or "partial" in block or "編碼" in block or "encoding" in block


def test_default_denied_scope_includes_prohibitions():
    builder = ScopeBuilder()
    block = builder.build_denied_scope([])
    assert any(word in block for word in ["partial", "encoding", "translation", "reconstruction", "片段", "編碼", "翻譯", "重構"])


def test_allowed_scope_returns_string():
    builder = ScopeBuilder()
    block = builder.build_allowed_scope(["test"])
    assert isinstance(block, str)
    assert len(block) > 0


def test_denied_scope_returns_string():
    builder = ScopeBuilder()
    block = builder.build_denied_scope(["test"])
    assert isinstance(block, str)
    assert len(block) > 0
