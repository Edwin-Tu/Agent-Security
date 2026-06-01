from dataclasses import dataclass, field

from .errors import InvalidModelOptionsError


@dataclass
class ModelOptions:
    temperature: float = 0.2
    top_p: float = 0.9
    num_ctx: int = 4096
    num_predict: int = 512
    seed: int | None = None
    stream: bool = True
    timeout_seconds: int = 60

    def __post_init__(self):
        if self.temperature < 0:
            raise InvalidModelOptionsError("temperature must be >= 0")
        if not (0 <= self.top_p <= 1):
            raise InvalidModelOptionsError("top_p must be between 0 and 1")
        if self.num_ctx <= 0:
            raise InvalidModelOptionsError("num_ctx must be > 0")
        if self.num_predict <= 0:
            raise InvalidModelOptionsError("num_predict must be > 0")
        if self.timeout_seconds <= 0:
            raise InvalidModelOptionsError("timeout_seconds must be > 0")
