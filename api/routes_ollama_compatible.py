from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from api.ollama_adapter import OllamaAdapter

router = APIRouter()


class GenerateRequest(BaseModel):
    model: str
    prompt: str = Field(..., min_length=1)
    stream: bool = False


class ChatRequestOllama(BaseModel):
    model: str
    messages: list[dict] = Field(..., min_length=1)
    stream: bool = False


adapter = OllamaAdapter()


@router.get("/api/tags")
def list_tags():
    return adapter.list_tags()


@router.post("/api/generate")
def generate(req: GenerateRequest):
    if req.stream:
        raise HTTPException(status_code=400, detail="stream=true is not yet supported")
    return adapter.generate(model=req.model, prompt=req.prompt)


@router.post("/api/chat")
def chat(req: ChatRequestOllama):
    if req.stream:
        raise HTTPException(status_code=400, detail="stream=true is not yet supported")
    return adapter.chat(model=req.model, messages=req.messages)
