from pathlib import Path

from .event_schema import GuardEvent
from .event_writer import EventWriter
from .event_redactor import EventRedactor


class EventLogger:
    def __init__(self, log_path: str | None = None):
        if log_path is None:
            log_path = str(Path(__file__).resolve().parent.parent / "logs" / "guard_events.jsonl")
        self.writer = EventWriter(log_path)
        self.redactor = EventRedactor()

    def log_event(self, event: GuardEvent | dict) -> GuardEvent:
        if isinstance(event, dict):
            event = GuardEvent.from_dict(event)
        event_dict = event.to_dict()
        redacted = self.redactor.redact_event(event_dict)
        self.writer.write(redacted)
        return event
