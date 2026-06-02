import builtins
import importlib

from config import Config
entry_main = importlib.import_module("entry.main")


class FakePipeline:
    def handle(self, prompt, model, dry_run):
        return {
            "success": True,
            "blocked": False,
            "safe_output": "A Python list is an ordered collection that can store multiple items in a single variable.",
        }


def test_ollama_cli_prints_safe_output_for_allow_request(monkeypatch, capsys):
    monkeypatch.setattr(builtins, "input", lambda prompt="": "please explain what a python list is in two sentences.")
    monkeypatch.setattr(entry_main, "SecretGuardPipeline", lambda cfg: FakePipeline())

    entry_main.ollama_mode(Config())

    captured = capsys.readouterr()
    assert "A Python list is an ordered collection" in captured.out
    assert "此內容受到限制" not in captured.out
