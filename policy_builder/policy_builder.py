from __future__ import annotations

from .policy_models import PolicyBuildInput, RequestProtectionPolicy
from .role_policy_resolver import resolve_role_authorization
from .policy_merger import merge_skill_defense_results
from .scope_builder import build_response_scope


def build_risk_level(risk_score: int) -> str:
    if risk_score <= 29:
        return "low"
    if risk_score <= 69:
        return "medium"
    return "high"


ACTION_MAPPING = {
    "ALLOW": {},
    "WARN": {},
    "REWRITE": {},
    "RESTRICT": {
        "verify_partial": True,
        "verify_reconstruction": True,
    },
    "BLOCK": {
        "refusal_strategy": "safe_refusal",
    },
    "AUTHORIZE": {
        "require_authorization": True,
    },
    "ESCALATE": {
        "runtime_monitoring_mode": "strict",
        "interrupt_on_match": True,
    },
}


class PolicyBuilder:
    def __init__(self):
        pass

    def build(self, input_data: PolicyBuildInput) -> RequestProtectionPolicy:
        risk_level = build_risk_level(input_data.risk_score)

        role_result = resolve_role_authorization(
            user_role=input_data.user_role,
            matched_assets=input_data.matched_assets,
            current_action=input_data.policy_action,
        )

        action = role_result["resolved_action"]
        require_authorization = role_result["require_authorization"]

        merged_skills = merge_skill_defense_results(
            enabled_skills=input_data.enabled_skills,
            skill_defense_results=input_data.skill_defense_results,
        )

        action_config = dict(ACTION_MAPPING.get(action, {}))
        if role_result.get("require_authorization"):
            action_config["require_authorization"] = True

        scope_result = build_response_scope(action, input_data.matched_assets)

        protected_asset_ids: list[str] = []
        protected_asset_names: list[str] = []
        protected_asset_types: list[str] = []
        all_protection_modes: list[str] = []
        restricted_tokens: list[str] = []
        has_high_risk = False

        for asset in input_data.matched_assets:
            aid = asset.get("asset_id")
            aname = asset.get("name")
            atype = asset.get("type")
            if aid:
                protected_asset_ids.append(aid)
            if aname:
                protected_asset_names.append(aname)
            if atype:
                protected_asset_types.append(atype)

            for mode in asset.get("protection_modes", []):
                if mode not in all_protection_modes:
                    all_protection_modes.append(mode)

            for alias in asset.get("aliases", []):
                if alias not in restricted_tokens:
                    restricted_tokens.append(alias)

            if asset.get("risk_level") in ("high", "critical"):
                has_high_risk = True

        verify_partial = action_config.get("verify_partial", False) or (
            has_high_risk and "partial_match" in all_protection_modes
        )
        verify_encoding = action_config.get("verify_encoding", False) or (
            merged_skills.get("verify_encoding", False)
        ) or (
            has_high_risk and "encoding_match" in all_protection_modes
        )
        verify_reconstruction = action_config.get("verify_reconstruction", False) or (
            merged_skills.get("verify_reconstruction", False)
        ) or (
            has_high_risk and "reconstruction_match" in all_protection_modes
        )
        verify_translation = action_config.get("verify_translation", False) or (
            has_high_risk and "translation_match" in all_protection_modes
        )

        runtime_mode = "strict" if action == "ESCALATE" else merged_skills.get("runtime_monitoring_mode", "normal")

        policy = RequestProtectionPolicy(
            request_id=input_data.request_id,
            action=action,
            risk_score=input_data.risk_score,
            risk_level=risk_level,
            user_role=input_data.user_role,
            attack_category=input_data.attack_category,
            protected_asset_ids=protected_asset_ids,
            protected_asset_names=protected_asset_names,
            protected_asset_types=protected_asset_types,
            protection_modes=all_protection_modes,
            allowed_response_scope=scope_result["allowed_response_scope"],
            denied_response_scope=scope_result["denied_response_scope"],
            enabled_skills=merged_skills["enabled_skills"],
            restricted_tokens=restricted_tokens + merged_skills.get("additional_restricted_tokens", []),
            blocked_transformations=merged_skills["blocked_transformations"],
            require_authorization=require_authorization or action_config.get("require_authorization", False),
            runtime_monitoring_enabled=True,
            runtime_monitoring_mode=runtime_mode,
            interrupt_on_match=action_config.get("interrupt_on_match", False),
            output_verification_enabled=True,
            verify_exact=True,
            verify_partial=verify_partial,
            verify_encoding=verify_encoding,
            verify_translation=verify_translation,
            verify_reconstruction=verify_reconstruction,
            refusal_strategy=action_config.get("refusal_strategy", "safe_refusal"),
        )

        return policy
