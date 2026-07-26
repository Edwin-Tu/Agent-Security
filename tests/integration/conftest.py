from __future__ import annotations

import os
import subprocess
from collections.abc import Iterator
from pathlib import Path

import pytest

from elder_privacy_guard.adapters import path_loader


def _resolve_agent_security_path(raw_path: str) -> Path:
    candidate = Path(raw_path).expanduser()
    if not candidate.is_absolute():
        candidate = (Path.cwd() / candidate).resolve()
    return candidate.resolve()


def _tracked_git_status(agent_security_path: Path) -> str:
    completed = subprocess.run(
        ["git", "status", "--short", "--untracked-files=no"],
        cwd=agent_security_path,
        check=True,
        env={**os.environ, "GIT_MASTER": "1"},
        capture_output=True,
        text=True,
    )
    return completed.stdout


@pytest.fixture(scope="session")
def agent_security_path() -> Iterator[Path]:
    raw_path = os.getenv("AGENT_SECURITY_PATH")
    if not raw_path:
        pytest.skip("AGENT_SECURITY_PATH is not set; skipping Agent-Security integration tests.")

    candidate = _resolve_agent_security_path(raw_path)
    if not candidate.is_dir():
        pytest.skip(f"AGENT_SECURITY_PATH does not point to a directory: {raw_path}")

    path_loader.reset()
    try:
        loaded_path = path_loader.load_agent_security_path(raw_path)
    except Exception as exc:
        pytest.skip(f"Agent-Security is unavailable at {raw_path}: {exc}")

    try:
        yield loaded_path
    finally:
        path_loader.reset()


@pytest.fixture(scope="session")
def agent_security_tracked_status(agent_security_path: Path) -> str:
    return _tracked_git_status(agent_security_path)


@pytest.fixture(autouse=True)
def connected_agent_security(
    agent_security_path: Path,
    agent_security_tracked_status: str,
) -> Iterator[None]:
    path_loader.reset()
    _ = path_loader.load_agent_security_path(str(agent_security_path))
    try:
        yield
    finally:
        current_status = _tracked_git_status(agent_security_path)
        path_loader.reset()

    assert current_status == agent_security_tracked_status
