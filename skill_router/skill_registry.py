from .skill_priority import DEFAULT_PRIORITY_ORDER


class SkillRegistry:
    def __init__(self):
        self._skills: dict[str, object] = {}
        self._categories: dict[str, list[str]] = {}
        self._priorities: dict[str, int] = {}

    def register(self, category: str, skill, priority: int | None = None) -> None:
        if priority is None:
            priority = DEFAULT_PRIORITY_ORDER.get(skill.name, 50)
        self._skills[skill.name] = skill
        if category not in self._categories:
            self._categories[category] = []
        if skill.name not in self._categories[category]:
            self._categories[category].append(skill.name)
        self._priorities[skill.name] = max(self._priorities.get(skill.name, 0), priority)

    def get(self, category: str) -> list[object]:
        skill_names = self._categories.get(category, [])
        result = []
        for name in skill_names:
            if name in self._skills:
                result.append(self._skills[name])
        return result

    def get_skill(self, name: str) -> object | None:
        return self._skills.get(name)

    def has(self, category: str) -> bool:
        return category in self._categories

    def list_categories(self) -> list[str]:
        return list(self._categories.keys())

    def get_priority(self, skill_name: str) -> int:
        return self._priorities.get(skill_name, 50)

    def set_priority(self, skill_name: str, priority: int) -> None:
        self._priorities[skill_name] = priority

    def get_all_skills(self) -> dict[str, object]:
        return dict(self._skills)
