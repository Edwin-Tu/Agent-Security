DEFAULT_PRIORITY_ORDER: dict[str, int] = {
    "SystemPromptExtractionSkill": 100,
    "DirectRequestSkill": 90,
    "InstructionOverrideSkill": 85,
    "EncodingBypassSkill": 80,
    "DataReconstructionSkill": 75,
    "PartialDisclosureSkill": 70,
    "MultiTurnProbeSkill": 65,
    "HomoglyphObfuscationSkill": 60,
    "RolePlaySkill": 55,
    "StructuredOutputSkill": 50,
}
