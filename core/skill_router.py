from typing import Optional


class SkillRouter:
    def __init__(self):
        self.skills: dict[str, object] = {}

    def register(self, skill):
        self.skills[skill.name] = skill

    def route(self, category: str) -> Optional[object]:
        skill_name = category.replace("_bypass", "").replace("_override", "").replace("_probe", "")
        for name, skill in self.skills.items():
            if name == category or name.startswith(skill_name):
                return skill
        return None

    def route_all(self, categories: list[str]) -> list[tuple[str, object]]:
        routed = []
        for cat in categories:
            skill = self.route(cat)
            if skill:
                routed.append((cat, skill))
        return routed

    def process(self, text: str, categories: list[str], context: dict = None) -> list[dict]:
        results = []
        for cat in categories:
            skill = self.route(cat)
            if skill:
                result = skill.process(text, context)
                results.append({"category": cat, "skill": skill.name, "result": result})
        return results
