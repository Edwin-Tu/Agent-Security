from __future__ import annotations

from .policy_models import RequestProtectionPolicy


def build_runtime_policy(policy: RequestProtectionPolicy) -> dict:
    asset_matchers = []
    for aid, aname, atype in zip(
        policy.protected_asset_ids,
        policy.protected_asset_names,
        policy.protected_asset_types,
        strict=False,
    ):
        asset_matchers.append({
            "asset_id": aid,
            "name": aname,
            "type": atype,
            "protection_modes": list(policy.protection_modes),
        })

    return {
        "internal_only": True,
        "request_id": policy.request_id,
        "asset_matchers": asset_matchers,
        "restricted_tokens": list(policy.restricted_tokens),
        "blocked_transformations": list(policy.blocked_transformations),
        "runtime_monitoring": {
            "enabled": policy.runtime_monitoring_enabled,
            "mode": policy.runtime_monitoring_mode,
            "interrupt_on_match": policy.interrupt_on_match,
        },
        "verification": {
            "exact": policy.verify_exact,
            "partial": policy.verify_partial,
            "encoding": policy.verify_encoding,
            "translation": policy.verify_translation,
            "reconstruction": policy.verify_reconstruction,
        },
    }
