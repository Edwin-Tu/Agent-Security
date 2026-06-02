from fastapi import APIRouter

from api.schemas import HealthResponse

router = APIRouter()

VERSION = "0.1.0"


@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", service="secretguard", version=VERSION)
