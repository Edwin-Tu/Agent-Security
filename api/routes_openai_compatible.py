from fastapi import APIRouter
from pydantic import BaseModel, Field

from api.openai_adapter import OpenAIAdapter

router = APIRouter()


class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[dict] = Field(..., min_length=1)
    stream: bool = False


adapter = OpenAIAdapter()


@router.post("/v1/chat/completions")
def chat_completions(req: ChatCompletionRequest):
    return adapter.chat_completion(
        model=req.model,
        messages=req.messages,
        stream=req.stream,
    )
