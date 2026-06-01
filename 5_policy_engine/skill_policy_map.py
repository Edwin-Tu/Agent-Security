from typing import Dict

SKILL_POLICY_MAP: Dict[str, str] = {
    "direct_secret_request": "direct_request_skill",
    "role_play": "role_play_skill",
    "instruction_override": "instruction_override_skill",
    "system_prompt_extraction": "system_prompt_extraction_skill",
    "encoding_bypass": "encoding_bypass_skill",
    "partial_disclosure": "partial_disclosure_skill",
    "translation_bypass": "translation_bypass_skill",
    "structured_output": "structured_output_skill",
    "log_access": "log_access_skill",
    "multi_turn_probe": "multi_turn_probe_skill",
    "policy_confusion": "policy_confusion_skill",
    "indirect_prompt_injection": "indirect_prompt_injection_skill",
    "format_smuggling": "format_smuggling_skill",
    "output_constraint_bypass": "output_constraint_bypass_skill",
    "reasoning_trap": "reasoning_trap_skill",
    "refusal_suppression": "refusal_suppression_skill",
    "persona_override": "persona_override_skill",
    "data_reconstruction": "data_reconstruction_skill",
    "cross_language_injection": "cross_language_injection_skill",
    "homoglyph_obfuscation": "homoglyph_obfuscation_skill",
}
