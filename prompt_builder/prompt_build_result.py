from dataclasses import dataclass, field


@dataclass
class PromptBuildResult:
    final_prompt: str
    system_guard_block: str
    user_task_block: str
    allowed_scope_block: str
    denied_scope_block: str
    refusal_instruction_block: str
    monitoring_hints: list[str] = field(default_factory=list)
    redacted_asset_refs: list[str] = field(default_factory=list)
    should_call_llm: bool = True
    safe_response: str | None = None
    build_metadata: dict = field(default_factory=dict)
