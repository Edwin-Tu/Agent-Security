import pytest
from defensive_skills.base_skill import BaseSkill
from defensive_skills.skill_models import SkillInput
from defensive_skills.direct_request_skill import DirectRequestSkill
from defensive_skills.instruction_override_skill import InstructionOverrideSkill
from defensive_skills.system_prompt_extraction_skill import SystemPromptExtractionSkill
from defensive_skills.encoding_bypass_skill import EncodingBypassSkill
from defensive_skills.partial_disclosure_skill import PartialDisclosureSkill
from defensive_skills.translation_bypass_skill import TranslationBypassSkill
from defensive_skills.multi_turn_probe_skill import MultiTurnProbeSkill


ALL_SKILLS = [
    DirectRequestSkill,
    InstructionOverrideSkill,
    SystemPromptExtractionSkill,
    EncodingBypassSkill,
    PartialDisclosureSkill,
    TranslationBypassSkill,
    MultiTurnProbeSkill,
]


class TestBaseSkillContract:
    def test_base_skill_raises_not_implemented(self):
        class IncompleteSkill(BaseSkill):
            pass

        skill = IncompleteSkill()
        inp = SkillInput(
            original_prompt="test",
            normalized_prompt="test",
            attack_category="test",
            policy_action="ALLOW",
        )
        with pytest.raises(NotImplementedError):
            skill.detect(inp)
        with pytest.raises(NotImplementedError):
            d = skill.detect(inp)
            skill.defend(inp, d)

    def test_all_skills_have_skill_name(self):
        for cls in ALL_SKILLS:
            skill = cls()
            assert hasattr(skill, 'skill_name')
            assert isinstance(skill.skill_name, str)
            assert len(skill.skill_name) > 0

    def test_all_skills_have_attack_categories(self):
        for cls in ALL_SKILLS:
            skill = cls()
            assert hasattr(skill, 'attack_categories')
            assert isinstance(skill.attack_categories, list)

    def test_all_skills_implement_detect(self):
        for cls in ALL_SKILLS:
            skill = cls()
            assert hasattr(skill, 'detect')
            assert callable(skill.detect)

    def test_all_skills_implement_defend(self):
        for cls in ALL_SKILLS:
            skill = cls()
            assert hasattr(skill, 'defend')
            assert callable(skill.defend)

    def test_detect_returns_detection_result(self):
        inp = SkillInput(
            original_prompt="test",
            normalized_prompt="test",
            attack_category="test",
            policy_action="ALLOW",
        )
        for cls in ALL_SKILLS:
            skill = cls()
            result = skill.detect(inp)
            from defensive_skills.skill_models import DetectionResult
            assert isinstance(result, DetectionResult)

    def test_defend_returns_defense_result(self):
        inp = SkillInput(
            original_prompt="test",
            normalized_prompt="test",
            attack_category="test",
            policy_action="ALLOW",
        )
        for cls in ALL_SKILLS:
            skill = cls()
            detection = skill.detect(inp)
            result = skill.defend(inp, detection)
            from defensive_skills.skill_models import DefenseResult
            assert isinstance(result, DefenseResult)
