from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping


class OwaspRisk(str, Enum):
    LLM01 = "LLM01_PROMPT_INJECTION"
    LLM02 = "LLM02_SENSITIVE_INFORMATION_DISCLOSURE"
    LLM07 = "LLM07_SYSTEM_PROMPT_LEAKAGE"


class PolicyAction(str, Enum):
    ALLOW = "ALLOW"
    SANITIZE = "SANITIZE"
    REQUIRE_AUTH = "REQUIRE_AUTH"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


@dataclass(frozen=True, slots=True)
class InputContext:
    source: str = "user"
    trusted: bool = True
    authenticated: bool = False
    authorized: bool = False
    role: str | None = None
    resource_owner: bool = False

    @classmethod
    def from_value(cls, value: object | None) -> "InputContext":
        if value is None:
            return cls()
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls(
                source=str(value.get("source", value.get("input_source", "user"))),
                trusted=bool(value.get("trusted", value.get("source_trust", True))),
                authenticated=bool(value.get("authenticated", False)),
                authorized=bool(value.get("authorized", False)),
                role=str(value["role"]) if value.get("role") is not None else None,
                resource_owner=bool(value.get("resource_owner", False)),
            )
        return cls()


@dataclass(slots=True)
class SecurityAssessment:
    action: PolicyAction
    risks: list[OwaspRisk] = field(default_factory=list)
    assets: list[str] = field(default_factory=list)
    intents: list[str] = field(default_factory=list)
    techniques: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    normalized_input: str = ""
    normalization_events: list[str] = field(default_factory=list)
    context: InputContext = field(default_factory=InputContext)

    def evidence(self) -> dict[str, object]:
        return {
            "guard_version": "elder-input-guard-llm01-02-07-v1.0",
            "owasp_risks": [risk.value for risk in self.risks],
            "detected_assets": list(self.assets),
            "intents": list(self.intents),
            "techniques": list(self.techniques),
            "authorization": {
                "source": "external_context",
                "authenticated": self.context.authenticated,
                "authorized": self.context.authorized,
                "resource_owner": self.context.resource_owner,
                "role": self.context.role,
            },
            "input_source": self.context.source,
            "source_trusted": self.context.trusted,
            "policy": {"action": self.action.value, "reasons": list(self.reasons)},
            "enforcement": {
                "model_called": self.action in {PolicyAction.ALLOW, PolicyAction.SANITIZE},
                "success": True,
            },
            "normalization_events": list(self.normalization_events),
        }


_ZERO_WIDTH = re.compile(r"[\u200b-\u200f\u202a-\u202e\u2060\ufeff]")
_MULTI_SPACE = re.compile(r"\s+")
_SEPARATOR_BETWEEN_LETTERS = re.compile(r"(?<=\w)[._\-](?=\w)")

_ASSET_PATTERNS: dict[str, tuple[str, ...]] = {
    "credential": (
        "api key", "apikey", "access token", "token", "password", "密碼", "金鑰", "憑證",
    ),
    "customer_profile": (
        "customer profile", "resident data", "customer data", "客戶資料", "住民資料", "長者資料",
    ),
    "personal_information": (
        "身分證", "電話", "地址", "住址", "email", "電子郵件", "個資", "personal information",
    ),
    "medical_record": (
        "病歷", "醫療紀錄", "用藥紀錄", "medical record", "health record", "diagnosis",
    ),
    "business_financial_data": (
        "財務資料", "營收", "成本", "business financial", "financial report",
    ),
    "core_secret": (
        "核心機密", "內部機密", "secret", "confidential data",
    ),
    "system_prompt": (
        "system prompt", "系統提示詞", "系統提示", "hidden instructions", "隱藏指令", "developer message",
        "開發者訊息", "internal instructions", "內部規則",
    ),
}

_OVERRIDE_PATTERNS = (
    r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions?|rules?)",
    r"disregard\s+(all\s+)?(previous|prior|above)",
    r"forget\s+(all\s+)?(previous|prior)\s+(instructions?|rules?)",
    r"忽略.{0,8}(之前|先前|以上|所有).{0,8}(指令|規則|提示)",
    r"(無視|不要理會).{0,12}(指令|規則|限制)",
    r"繞過.{0,8}(安全|限制|規則|防護)",
)

_ROLE_PATTERNS = (
    r"you are now", r"act as", r"developer mode", r"jailbreak", r"dan mode",
    r"你現在是", r"請扮演.{0,12}(管理員|開發者|系統)", r"進入.{0,8}(開發者|無限制|越獄)模式",
)

_PROMPT_CLAIM_PATTERNS = (
    r"我是.{0,10}(管理員|醫師|醫生|主管|安全團隊|開發者)",
    r"(主管|管理員|安全團隊).{0,12}(批准|授權|同意)",
    r"i am (an? )?(admin|administrator|doctor|developer)",
    r"(manager|security team).{0,12}(approved|authorized)",
)

_REQUEST_PATTERNS = (
    r"(請|幫我|我要|給我|提供|顯示|告訴|念出|讀出|列出|匯出|輸出|回傳|揭露|透露|取得|查出)",
    r"\b(show|give|provide|reveal|tell|read|list|export|output|return|retrieve|extract|display)\b",
)

_SAFE_DISCUSSION_PATTERNS = (
    r"(如何|怎麼|為什麼|說明|解釋|分析|避免|防止|保護|風險|最佳實務)",
    r"\b(how|why|explain|analy[sz]e|prevent|protect|risk|best practice)\b",
)

_PARTIAL_PATTERNS = (
    r"(前|後|頭|尾).{0,5}(\d+|一|二|三|四|五).{0,4}(字|碼|位|個)",
    r"first\s+\d+", r"last\s+\d+", r"partial", r"部分",
)

_TRANSFORM_PATTERNS: dict[str, tuple[str, ...]] = {
    "encoded": ("base64", "hex", "編碼", "加密後輸出"),
    "reversed": ("reverse", "reversed", "反轉", "倒序"),
    "split": ("split", "拆分", "分組", "逐字", "一個字一個字"),
    "structured_export": ("json", "csv", "xml", "表格", "結構化", "匯出"),
}

_PROMPT_LEAK_REQUESTS = (
    r"(顯示|提供|揭露|輸出|重複|告訴我|列出|讀出).{0,20}(系統提示|系統提示詞|隱藏指令|內部規則|開發者訊息)",
    r"(system prompt|hidden instructions?|developer message|internal instructions?).{0,20}(show|reveal|repeat|print|give|tell)",
    r"(show|reveal|repeat|print|give|tell).{0,20}(system prompt|hidden instructions?|developer message|internal instructions?)",
)

_INDIRECT_INSTRUCTION_PATTERNS = (
    r"(以下|下方|文件中|行事曆中|網頁中|郵件中).{0,20}(指令|命令).{0,10}(執行|遵守|照做)",
    r"treat.{0,20}(document|calendar|email|webpage|content).{0,20}as.{0,10}(instruction|command)",
)


def normalize_for_security(text: str) -> tuple[str, list[str]]:
    events: list[str] = []
    normalized = unicodedata.normalize("NFKC", text)
    if normalized != text:
        events.append("unicode_nfkc")
    stripped = _ZERO_WIDTH.sub("", normalized)
    if stripped != normalized:
        events.append("removed_invisible_characters")
    collapsed = _MULTI_SPACE.sub(" ", stripped).strip().lower()
    if collapsed != stripped:
        events.append("collapsed_whitespace_and_casefolded")
    deobfuscated = _SEPARATOR_BETWEEN_LETTERS.sub("", collapsed)
    if deobfuscated != collapsed:
        events.append("removed_intra_token_separators")
    return deobfuscated, events


def assess_input(text: str, context: object | None = None) -> SecurityAssessment:
    normalized, events = normalize_for_security(text)
    ctx = InputContext.from_value(context)
    assets = _detect_assets(normalized)
    risks: list[OwaspRisk] = []
    intents: list[str] = []
    techniques: list[str] = []
    reasons: list[str] = []

    meta_discussion = _is_meta_discussion(normalized)
    self_supplied_data = _is_self_supplied_data(normalized)
    override = _matches_any(normalized, _OVERRIDE_PATTERNS) and not meta_discussion
    role_hijack = _matches_any(normalized, _ROLE_PATTERNS) and not meta_discussion
    indirect_instruction = _matches_any(normalized, _INDIRECT_INSTRUCTION_PATTERNS)
    prompt_claim_only = _matches_any(normalized, _PROMPT_CLAIM_PATTERNS)

    if override:
        risks.append(OwaspRisk.LLM01)
        techniques.append("instruction_override")
        reasons.append("instruction_override_detected")
    if role_hijack:
        _append_unique(risks, OwaspRisk.LLM01)
        techniques.append("role_hijacking")
        reasons.append("role_hijacking_detected")
    if indirect_instruction and not ctx.trusted:
        _append_unique(risks, OwaspRisk.LLM01)
        techniques.append("indirect_prompt_injection")
        reasons.append("untrusted_content_contains_executable_instruction")
    if prompt_claim_only:
        techniques.append("prompt_claim_only")
        reasons.append("prompt_authorization_claim_not_trusted")

    prompt_leak = (
        any(re.search(pattern, normalized, re.I) for pattern in _PROMPT_LEAK_REQUESTS)
        and not meta_discussion
        and not _is_public_prompt_example_request(normalized)
    )
    if prompt_leak:
        _append_unique(risks, OwaspRisk.LLM07)
        intents.append("SYSTEM_PROMPT_DISCLOSURE_REQUEST")
        techniques.append("system_prompt_extraction")
        reasons.append("system_prompt_disclosure_requested")

    request = _matches_any(normalized, _REQUEST_PATTERNS)
    safe_discussion = _matches_any(normalized, _SAFE_DISCUSSION_PATTERNS)
    protected_assets = [asset for asset in assets if asset != "system_prompt"]

    if protected_assets and request and not self_supplied_data:
        if safe_discussion and not _has_extraction_signal(normalized):
            intents.append("BENIGN_SECURITY_DISCUSSION")
        else:
            disclosure_intent = _classify_disclosure_intent(normalized)
            intents.append(disclosure_intent)
            _append_unique(risks, OwaspRisk.LLM02)
            reasons.append("protected_asset_with_disclosure_intent")
            techniques.extend(_detect_techniques(normalized))
    elif protected_assets and safe_discussion:
        intents.append("BENIGN_SECURITY_DISCUSSION")
    elif protected_assets:
        intents.append("MENTION")

    if prompt_claim_only and protected_assets and request and not ctx.authorized:
        _append_unique(risks, OwaspRisk.LLM02)

    action = _decide_action(
        risks=risks,
        intents=intents,
        techniques=techniques,
        context=ctx,
        has_prompt_claim=prompt_claim_only,
    )

    return SecurityAssessment(
        action=action,
        risks=risks,
        assets=assets,
        intents=intents,
        techniques=_dedupe(techniques),
        reasons=_dedupe(reasons),
        normalized_input=normalized,
        normalization_events=events,
        context=ctx,
    )



def _is_meta_discussion(text: str) -> bool:
    discussion_markers = (
        "什麼是", "是什麼", "概念", "如何防止", "如何避免", "為何", "為什麼",
        "解釋", "說明", "分析", "風險", "危險字串", "介紹",
        "what is", "explain", "analyze", "analyse", "why", "risk", "concept",
    )
    return any(marker in text for marker in discussion_markers)


def _is_public_prompt_example_request(text: str) -> bool:
    public_markers = ("虛構", "範例", "example", "fictional", "public sample")
    return any(marker in text for marker in public_markers)


def _is_self_supplied_data(text: str) -> bool:
    patterns = (
        r"我的.{0,8}(電話|地址|住址|email|電子郵件).{0,4}(是|為|:|：)",
        r"my\s+(phone|address|email).{0,4}(is|:)",
    )
    return _matches_any(text, patterns)


def _detect_assets(text: str) -> list[str]:
    found: list[str] = []
    for asset, terms in _ASSET_PATTERNS.items():
        if any(term in text for term in terms):
            found.append(asset)
    return found


def _detect_techniques(text: str) -> list[str]:
    found = ["direct"]
    if _matches_any(text, _PARTIAL_PATTERNS):
        found = ["partial"]
    for technique, terms in _TRANSFORM_PATTERNS.items():
        if any(term in text for term in terms):
            found.append(technique)
    return _dedupe(found)


def _classify_disclosure_intent(text: str) -> str:
    if _matches_any(text, _PARTIAL_PATTERNS):
        return "PARTIAL_DISCLOSURE_REQUEST"
    if any(term in text for values in _TRANSFORM_PATTERNS.values() for term in values):
        return "TRANSFORMED_DISCLOSURE_REQUEST"
    return "DIRECT_DISCLOSURE_REQUEST"


def _has_extraction_signal(text: str) -> bool:
    return bool(
        _matches_any(text, _PARTIAL_PATTERNS)
        or any(term in text for values in _TRANSFORM_PATTERNS.values() for term in values)
        or any(term in text for term in ("目前的", "實際的", "完整", "所有", "全部", "current", "actual", "full value"))
    )


def _decide_action(
    *,
    risks: list[OwaspRisk],
    intents: list[str],
    techniques: list[str],
    context: InputContext,
    has_prompt_claim: bool,
) -> PolicyAction:
    if OwaspRisk.LLM07 in risks:
        return PolicyAction.BLOCK
    if OwaspRisk.LLM01 in risks:
        return PolicyAction.BLOCK

    disclosure = any(intent.endswith("DISCLOSURE_REQUEST") for intent in intents)
    if disclosure:
        high_risk_technique = any(t in techniques for t in ("partial", "encoded", "reversed", "split"))
        if high_risk_technique or has_prompt_claim:
            return PolicyAction.BLOCK
        if context.authorized or context.resource_owner:
            return PolicyAction.ALLOW
        if context.authenticated:
            return PolicyAction.REQUIRE_AUTH
        return PolicyAction.BLOCK

    return PolicyAction.ALLOW


def _matches_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, re.I) for pattern in patterns)


def _append_unique(items: list, value: object) -> None:
    if value not in items:
        items.append(value)


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))
