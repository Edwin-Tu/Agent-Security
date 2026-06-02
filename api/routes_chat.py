import json
from typing import Generator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from api.schemas import ChatRequest, ChatResponse
from entry.secretguard_pipeline import SecretGuardPipeline
from llm_gateway.ollama_provider import OllamaProvider

router = APIRouter()

pipeline = SecretGuardPipeline()


@router.post("/v1/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    provider = OllamaProvider()
    return pipeline.chat(req, provider)


@router.post("/v1/chat/stream")
def chat_stream(req: ChatRequest):
    provider = OllamaProvider()

    def event_stream() -> Generator[str, None, None]:
        for event in pipeline.chat_stream(req, provider):
            yield json.dumps(event, ensure_ascii=False) + "\n"

    return StreamingResponse(
        event_stream(),
        media_type="application/x-ndjson",
    )
