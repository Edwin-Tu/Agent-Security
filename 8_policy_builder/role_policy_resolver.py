from __future__ import annotations


def resolve_role_authorization(
    user_role: str,
    matched_assets: list[dict],
    current_action: str,
) -> dict:
    require_authorization = False
    denied_scope: list[str] = []
    resolved_action = current_action

    for asset in matched_assets:
        allowed_roles = asset.get("allowed_roles")
        if allowed_roles is None:
            allowed_roles = ["owner"]

        if user_role not in allowed_roles:
            require_authorization = True
            asset_name = asset.get("name", "protected asset")
            denied_scope.append(f"不可提供受保護資產「{asset_name}」的內容")

    if require_authorization and current_action not in ("AUTHORIZE", "BLOCK"):
        resolved_action = "AUTHORIZE"

    return {
        "require_authorization": require_authorization,
        "denied_response_scope": denied_scope,
        "resolved_action": resolved_action,
    }
