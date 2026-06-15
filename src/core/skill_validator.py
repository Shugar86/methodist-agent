import re
from pathlib import Path
from typing import List

from core.skill_registry import SkillRegistry


class SkillValidator:
    def __init__(self, skills_dir: Path):
        self.registry = SkillRegistry(skills_dir)

    def validate_all(self) -> List[str]:
        errors = []
        seen = set()
        for key, skill in self.registry.catalog.items():
            if not skill.name:
                errors.append(f"{key}: missing name")
            elif not re.fullmatch(r"[a-z0-9-]+", skill.name):
                errors.append(f"{key}: invalid name '{skill.name}'")

            if not skill.description:
                errors.append(f"{key}: missing description")
            elif len(skill.description) > 1024:
                errors.append(f"{key}: description too long")

            if skill.name and skill.name in seen:
                errors.append(f"{key}: duplicate name '{skill.name}'")
            if skill.name:
                seen.add(skill.name)

        return errors
