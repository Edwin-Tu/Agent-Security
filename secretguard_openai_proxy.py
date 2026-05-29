from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Any
import time

from config import Config
from entry.secretguard_pipeline import SecretGuardPipeline


app = FastAPI(title="SecretGuard OpenAI-Compatible Proxy")

cfg = Config()
pipeline = SecretGuardPipeline(cfg)


@app.get("/v1/models")
def list_models():
    model_name = cfg.model or "gemma3:12b"

    return {
        "object": "list",
        "data": [
            {
                "id": model_name,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "secretguard-ollama",
            }
        ],
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()

    model = body.get("model") or cfg.model
    messages = body.get("messages", [])

    if not messages:
        raise HTTPException(status_code=400, detail="messages is required")

    user_prompt_parts = []

    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")

        if isinstance(content, list):
            content = "\n".join(
                part.get("text", "")
                for part in content
                if isinstance(part, dict) and part.get("type") == "text"
            )

        if role == "system":
            user_prompt_parts.append(f"[System]\n{content}")
        elif role == "user":
            user_prompt_parts.append(f"[User]\n{content}")
        elif role == "assistant":
            user_prompt_parts.append(f"[Assistant]\n{content}")

    prompt = "\n\n".join(user_prompt_parts).strip()

    result = pipeline.handle(
        prompt=prompt,
        model=model,
        dry_run=False,
    )

    safe_output = result.get("safe_output") or "[SecretGuard] No output."

    return JSONResponse(
        {
            "id": f"chatcmpl-secretguard-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": safe_output,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            "secretguard": {
                "blocked": result.get("blocked"),
                "policy_action": result.get("policy_action"),
                "risk_score": result.get("risk_score"),
                "risk_level": result.get("risk_level"),
                "attack_categories": result.get("attack_categories"),
                "enabled_skills": result.get("enabled_skills"),
                "leakage_detected": result.get("leakage_detected"),
                "final_response_type": result.get("final_response_type"),
            },
        }
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": cfg.model,
        "ollama_url": cfg.ollama_url,
    }