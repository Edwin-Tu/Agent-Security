from dataclasses import dataclass, field


@dataclass
class OllamaModelInfo:
    name: str
    modified_at: str = ""
    size: int = 0


@dataclass
class LLMChunk:
    text: str
    model: str
    done: bool = False
    raw: dict | None = None
    stopped_by_guard: bool = False


@dataclass
class LLMResponse:
    success: bool
    text: str
    model: str
    done: bool
    error_type: str | None = None
    error_message: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_duration_ms: int | None = None
    stopped_by_guard: bool = False
    raw: dict | None = None
