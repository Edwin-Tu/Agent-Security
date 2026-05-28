from typing import Optional


class SkillRouter:
    def __init__(self):
        self.skills: dict[str, object] = {}
        self.category_map: dict[str, list[str]] = {}
        self.priority_map: dict[str, int] = {}

    def register(self, skill):
        self.skills[skill.name] = skill

    def register_with_priority(self, skill, priority: int = 0):
        self.skills[skill.name] = skill
        self.priority_map[skill.name] = priority

    def map_category(self, category: str, skill_names: list[str]):
        self.category_map[category] = skill_names

    def route(self, category: str) -> Optional[object]:
        if category in self.category_map:
            skill_names = self.category_map[category]
            skill_names.sort(key=lambda n: self.priority_map.get(n, 0), reverse=True)
            for name in skill_names:
                if name in self.skills:
                    return self.skills[name]
            return None
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
        seen_skills = set()
        for cat in categories:
            skill = self.route(cat)
            if skill and id(skill) not in seen_skills:
                seen_skills.add(id(skill))
                result = skill.process(text, context)
                results.append({"category": cat, "skill": skill.name, "result": result})
        return results

    def get_skills_by_category(self, category: str) -> list[str]:
        return self.category_map.get(category, [])
