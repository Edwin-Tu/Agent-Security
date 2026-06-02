from enum import Enum


class PolicyAction(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    REWRITE = "REWRITE"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"
    AUTHORIZE = "AUTHORIZE"
    ESCALATE = "ESCALATE"
