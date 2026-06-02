from fastapi import APIRouter

from api.schemas import AnalyzeRequest, AnalyzeResponse
from entry.secretguard_pipeline import SecretGuardPipeline

router = APIRouter()

pipeline = SecretGuardPipeline()


@router.post("/v1/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    decision = pipeline.analyze(
        prompt=req.prompt,
        session_id=req.session_id,
        role=req.role,
    )
    return AnalyzeResponse(
        allowed=decision.allowed,
        action=decision.action,
        risk_score=decision.risk_score,
        attack_type=decision.attack_type,
        reason=decision.reason,
        matched_assets=decision.matched_assets,
    )
