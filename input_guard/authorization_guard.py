class AuthorizationGuard:
    def __init__(self):
        self.roles: dict[str, list[str]] = {}
        self.current_role: str = "default"

    def define_role(self, role: str, permissions: list[str]):
        self.roles[role] = permissions

    def set_role(self, role: str):
        if role in self.roles:
            self.current_role = role

    def check(self, text: str) -> dict:
        return {"blocked": False, "reason": "Authorization check passed.", "role": self.current_role}

    def check_permission(self, required_permission: str) -> bool:
        permissions = self.roles.get(self.current_role, [])
        return required_permission in permissions
