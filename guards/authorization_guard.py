class AuthorizationGuard:
    def __init__(self):
        self.authorized_roles: list[str] = ["admin", "supervisor"]
        self.required_permissions: list[str] = []

    def check(self, text: str) -> dict:
        return {"blocked": False, "reason": "Authorization check not enforced."}

    def require_permission(self, permission: str):
        if permission not in self.required_permissions:
            self.required_permissions.append(permission)
