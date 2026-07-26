from __future__ import annotations

import os
import sys
from pathlib import Path

EXPECTED_MODULES = [
    "input_normalization",
    "input_guard",
    "attack_classifier",
    "intent_classifier",
]

_loaded_path: Path | None = None


class AgentSecurityNotFoundError(FileNotFoundError):
    pass


class AgentSecurityIncompleteError(RuntimeError):
    pass


def load_agent_security_path(path_override: str | None = None) -> Path:
    candidate_text = path_override if path_override is not None else os.getenv("AGENT_SECURITY_PATH")
    if not candidate_text:
        raise AgentSecurityNotFoundError("AGENT_SECURITY_PATH is not set")

    candidate_path = Path(candidate_text).expanduser()
    if not candidate_path.is_absolute():
        candidate_path = (Path.cwd() / candidate_path).resolve()
    else:
        candidate_path = candidate_path.resolve()

    if not candidate_path.exists():
        raise AgentSecurityNotFoundError(f"Agent-Security path not found: {candidate_text}")
    if not candidate_path.is_dir():
        raise AgentSecurityNotFoundError(f"Agent-Security path not found: {candidate_text}")

    missing_modules = [
        module_name
        for module_name in EXPECTED_MODULES
        if not _module_exists(candidate_path, module_name)
    ]
    if missing_modules:
        missing_text = ", ".join(missing_modules)
        raise AgentSecurityIncompleteError(
            f"Agent-Security path is missing required modules: {missing_text}"
        )

    _set_loaded_path(candidate_path)
    return candidate_path


def get_agent_security_path() -> Path | None:
    return _loaded_path


def is_agent_security_available() -> bool:
    return _loaded_path is not None


def reset() -> None:
    global _loaded_path

    if _loaded_path is not None:
        _remove_sys_path_entry(_loaded_path)
    _loaded_path = None


def _module_exists(root: Path, module_name: str) -> bool:
    return (root / f"{module_name}.py").exists() or (root / module_name / "__init__.py").exists()


def _set_loaded_path(path: Path) -> None:
    global _loaded_path

    if _loaded_path is not None and _loaded_path != path:
        _remove_sys_path_entry(_loaded_path)

    path_text = str(path)
    if path_text in sys.path:
        sys.path.remove(path_text)
    sys.path.insert(0, path_text)
    _loaded_path = path


def _remove_sys_path_entry(path: Path) -> None:
    path_text = str(path)
    while path_text in sys.path:
        sys.path.remove(path_text)
