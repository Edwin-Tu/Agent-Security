from __future__ import annotations

import sys
from pathlib import Path

import pytest

import elder_privacy_guard.adapters.path_loader as path_loader


EXPECTED_MODULES = [
    "input_normalization",
    "input_guard",
    "attack_classifier",
    "intent_classifier",
]


def _create_agent_security_tree(root: Path) -> Path:
    _ = root.mkdir(parents=True, exist_ok=True)
    for module_name in EXPECTED_MODULES:
        _ = (root / f"{module_name}.py").write_text("\n", encoding="utf-8")
    return root


def test_load_agent_security_path_raises_when_path_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AGENT_SECURITY_PATH", raising=False)
    path_loader.reset()

    with pytest.raises(path_loader.AgentSecurityNotFoundError, match="AGENT_SECURITY_PATH"):
        _ = path_loader.load_agent_security_path()


def test_load_agent_security_path_raises_when_override_path_missing(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing-agent-security"
    path_loader.reset()

    with pytest.raises(path_loader.AgentSecurityNotFoundError, match=str(missing_path)):
        _ = path_loader.load_agent_security_path(str(missing_path))


def test_load_agent_security_path_raises_when_expected_modules_are_missing(tmp_path: Path) -> None:
    agent_security_root = tmp_path / "agent-security"
    _ = agent_security_root.mkdir()
    _ = (agent_security_root / "input_normalization.py").write_text("\n", encoding="utf-8")
    _ = (agent_security_root / "input_guard.py").write_text("\n", encoding="utf-8")
    path_loader.reset()

    with pytest.raises(path_loader.AgentSecurityIncompleteError) as exc_info:
        _ = path_loader.load_agent_security_path(str(agent_security_root))

    message = str(exc_info.value)
    assert "attack_classifier" in message
    assert "intent_classifier" in message


def test_load_agent_security_path_supports_relative_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    agent_security_root = _create_agent_security_tree(tmp_path / "agent-security")
    monkeypatch.chdir(tmp_path)
    path_loader.reset()

    loaded_path = path_loader.load_agent_security_path("agent-security")

    assert loaded_path == agent_security_root
    assert path_loader.get_agent_security_path() == agent_security_root
    assert path_loader.is_agent_security_available() is True
    assert sys.path[0] == str(agent_security_root)


def test_load_agent_security_path_expands_home_directory(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    home_dir = tmp_path / "home"
    agent_security_root = _create_agent_security_tree(home_dir / "agent-security")
    monkeypatch.setenv("HOME", str(home_dir))
    path_loader.reset()

    loaded_path = path_loader.load_agent_security_path("~/agent-security")

    assert loaded_path == agent_security_root
    assert path_loader.get_agent_security_path() == agent_security_root


def test_load_agent_security_path_does_not_duplicate_sys_path_entries(tmp_path: Path) -> None:
    agent_security_root = _create_agent_security_tree(tmp_path / "agent-security")
    path_loader.reset()

    _ = path_loader.load_agent_security_path(str(agent_security_root))
    _ = path_loader.load_agent_security_path(str(agent_security_root))

    assert sys.path.count(str(agent_security_root)) == 1


def test_reset_clears_loader_state_and_availability(tmp_path: Path) -> None:
    agent_security_root = _create_agent_security_tree(tmp_path / "agent-security")
    path_loader.reset()

    _ = path_loader.load_agent_security_path(str(agent_security_root))
    assert path_loader.is_agent_security_available() is True

    path_loader.reset()

    assert path_loader.get_agent_security_path() is None
    assert path_loader.is_agent_security_available() is False
    assert str(agent_security_root) not in sys.path
