import pytest
import json
from pathlib import Path
from event_logger.event_writer import EventWriter


class TestEventWriter:

    def test_auto_creates_log_directory(self, tmp_path):
        log_path = str(tmp_path / "sub" / "events.jsonl")
        writer = EventWriter(log_path)
        writer.write({"test": True})
        assert Path(log_path).exists()

    def test_appends_one_line_per_write(self, tmp_path):
        log_path = str(tmp_path / "events.jsonl")
        writer = EventWriter(log_path)
        writer.write({"id": 1})
        writer.write({"id": 2})
        with open(log_path, "r") as f:
            lines = f.readlines()
        assert len(lines) == 2

    def test_multiple_writes_do_not_overwrite(self, tmp_path):
        log_path = str(tmp_path / "events.jsonl")
        writer = EventWriter(log_path)
        writer.write({"seq": 1})
        writer.write({"seq": 2})
        writer.write({"seq": 3})
        with open(log_path, "r") as f:
            events = [json.loads(line) for line in f]
        assert len(events) == 3
        assert events[0]["seq"] == 1
        assert events[2]["seq"] == 3

    def test_written_content_is_utf8(self, tmp_path):
        log_path = str(tmp_path / "events.jsonl")
        writer = EventWriter(log_path)
        writer.write({"text": "測試中文"})
        with open(log_path, "r", encoding="utf-8") as f:
            line = f.readline()
        data = json.loads(line)
        assert data["text"] == "測試中文"

    def test_written_content_is_valid_json(self, tmp_path):
        log_path = str(tmp_path / "events.jsonl")
        writer = EventWriter(log_path)
        writer.write({"key": "value", "num": 42})
        with open(log_path, "r") as f:
            data = json.loads(f.readline())
        assert data["key"] == "value"
        assert data["num"] == 42
