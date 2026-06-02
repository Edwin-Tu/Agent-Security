from dataclasses import dataclass, field


@dataclass
class PipelineContext:
    prompt: str
    normalized_prompt: str | None = None
    session_id: str = "default"
    role: str = "user"
    metadata: dict = field(default_factory=dict)
