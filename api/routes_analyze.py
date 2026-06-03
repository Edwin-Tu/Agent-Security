from fastapi import APIRouter

from api.schemas import AnalyzeRequest, AnalyzeResponse, IntentMetadata
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
    intent_meta = None
    if decision.intent_result:
        intent_meta = IntentMetadata(
            intent=decision.intent_result.get("intent"),
            operation=decision.intent_result.get("operation"),
            scope=decision.intent_result.get("scope"),
            disclosure_mode=decision.intent_result.get("disclosure_mode"),
            asset_reference_type=decision.intent_result.get("asset_reference_type"),
            intent_risk_score=decision.intent_result.get("risk_score"),
            confidence=decision.intent_result.get("confidence"),
            reasons=decision.intent_result.get("reasons", []),
        )
    return AnalyzeResponse(
        allowed=decision.allowed,
        action=decision.action,
        risk_score=decision.risk_score,
        attack_type=decision.attack_type,
        reason=decision.reason,
        matched_assets=decision.matched_assets,
        intent=intent_meta,
    )
