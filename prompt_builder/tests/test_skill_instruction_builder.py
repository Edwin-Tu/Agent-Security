from prompt_builder.skill_instruction_builder import SkillInstructionBuilder


def test_partial_disclosure_skill():
    builder = SkillInstructionBuilder()
    result = builder.build(["PartialDisclosureSkill"])
    assert "部分揭露" in result or "partial disclosure" in result or "partial" in result


def test_encoding_bypass_skill():
    builder = SkillInstructionBuilder()
    result = builder.build(["EncodingBypassSkill"])
    assert "Base64" in result or "base64" in result or "Hex" in result or "hex" in result or "ROT13" in result or "rot13" in result


def test_translation_bypass_skill():
    builder = SkillInstructionBuilder()
    result = builder.build(["TranslationBypassSkill"])
    assert "翻譯" in result or "translation" in result


def test_system_prompt_extraction_skill():
    builder = SkillInstructionBuilder()
    result = builder.build(["SystemPromptExtractionSkill"])
    assert "system prompt" in result or "System Prompt" in result or "系統提示" in result


def test_unknown_skill_does_not_crash():
    builder = SkillInstructionBuilder()
    result = builder.build(["UnknownSkill123"])
    assert isinstance(result, str)


def test_multiple_skills_combined():
    builder = SkillInstructionBuilder()
    result = builder.build(["PartialDisclosureSkill", "EncodingBypassSkill"])
    assert "部分揭露" in result or "partial" in result
    assert "Base64" in result or "base64" in result


def test_all_known_skills():
    builder = SkillInstructionBuilder()
    skills = [
        "DirectRequestSkill",
        "PartialDisclosureSkill",
        "EncodingBypassSkill",
        "TranslationBypassSkill",
        "SystemPromptExtractionSkill",
        "InstructionOverrideSkill",
        "RolePlaySkill",
        "DataReconstructionSkill",
    ]
    result = builder.build(skills)
    assert isinstance(result, str)
    assert len(result) > 0


def test_empty_skills():
    builder = SkillInstructionBuilder()
    result = builder.build([])
    assert result == "" or result is None or isinstance(result, str)
