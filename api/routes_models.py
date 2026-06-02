from fastapi import APIRouter

from api.schemas import ModelInfo, ModelsResponse
from llm_gateway.ollama_provider import OllamaProvider
from llm_gateway.base_provider import ProviderError

router = APIRouter()

provider = OllamaProvider()


@router.get("/v1/models", response_model=ModelsResponse)
def list_models():
    try:
        models_data = provider.list_models()
        models = [ModelInfo(name=m["name"]) for m in models_data]
        return ModelsResponse(provider="ollama", models=models)
    except ProviderError as e:
        return ModelsResponse(
            provider="ollama",
            models=[],
            error="provider_error",
            message=str(e),
        )
    except Exception as e:
        return ModelsResponse(
            provider="ollama",
            models=[],
            error="provider_error",
            message=str(e),
        )
