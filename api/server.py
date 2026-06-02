from fastapi import FastAPI

from api.routes_health import router as health_router
from api.routes_analyze import router as analyze_router
from api.routes_models import router as models_router
from api.routes_chat import router as chat_router
from api.routes_openai_compatible import router as openai_router
from api.routes_ollama_compatible import router as ollama_router

app = FastAPI(title="SecretGuard API")

app.include_router(health_router)
app.include_router(analyze_router)
app.include_router(models_router)
app.include_router(chat_router)
app.include_router(openai_router)
app.include_router(ollama_router)
