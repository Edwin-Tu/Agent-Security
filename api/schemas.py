from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class AnalyzeRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    session_id: str = "default"
    role: str = "user"


class IntentMetadata(BaseModel):
    intent: str | None = None
    operation: str | None = None
    scope: str | None = None
    disclosure_mode: str | None = None
    asset_reference_type: str | None = None
    intent_risk_score: int | None = None
    confidence: float | None = None
    reasons: list[str] = []


class AnalyzeResponse(BaseModel):
    allowed: bool
    action: str
    risk_score: int
    attack_type: str | None = None
    reason: str | None = None
    matched_assets: list[dict[str, Any]] = Field(default_factory=list)
    intent: IntentMetadata | None = None


class ModelInfo(BaseModel):
    name: str


class ModelsResponse(BaseModel):
    provider: str
    models: list[ModelInfo] = Field(default_factory=list)
    error: str | None = None
    message: str | None = None


class ChatRequest(BaseModel):
    model: str
    prompt: str = Field(..., min_length=1)
    session_id: str = "default"
    role: str = "user"
    stream: bool = False
    options: dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    allowed: bool
    action: str
    risk_score: int
    attack_type: str | None = None
    response: str = ""
    blocked_reason: str | None = None
    event_id: str | None = None
    error: str | None = None
    error_message: str | None = None
