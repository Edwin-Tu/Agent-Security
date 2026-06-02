import builtins
import importlib

from config import Config
from entry.guard_result import GuardDecision
from entry.secretguard_pipeline import SecretGuardPipeline as OriginalPipeline

entry_main = importlib.import_module("entry.main")


def test_ollama_cli_accepts_normal_prompt(monkeypatch, capsys):
    monkeypatch.setattr(builtins, "input", lambda prompt="": "please explain what a python list is")

    def fake_pipeline(cfg):
        p = OriginalPipeline(cfg)
        p.analyze = lambda prompt, session_id="default", role="user": GuardDecision(
            allowed=True, action="allow", risk_score=0, attack_type=None, reason=None,
        )
        return p

    monkeypatch.setattr(entry_main, "SecretGuardPipeline", fake_pipeline)
    entry_main.ollama_mode(Config())
    captured = capsys.readouterr()
    assert "Input accepted" in captured.out
