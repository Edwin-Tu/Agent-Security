from __future__ import annotations

from .policy_models import RequestProtectionPolicy


def build_prompt_safe_policy(policy: RequestProtectionPolicy) -> dict:
    return {
        "request_id": policy.request_id,
        "action": policy.action,
        "risk_score": policy.risk_score,
        "risk_level": policy.risk_level,
        "user_role": policy.user_role,
        "attack_category": policy.attack_category,
        "protected_asset_ids": list(policy.protected_asset_ids),
        "protected_asset_names": list(policy.protected_asset_names),
        "protected_asset_types": list(policy.protected_asset_types),
        "protection_modes": list(policy.protection_modes),
        "allowed_response_scope": list(policy.allowed_response_scope),
        "denied_response_scope": list(policy.denied_response_scope),
        "refusal_strategy": policy.refusal_strategy,
    }
