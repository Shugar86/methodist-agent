from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class SkillV2:
    name: str
    description: str
    path: Path
    triggers: List[str] = field(default_factory=list)
    examples: List[Dict[str, str]] = field(default_factory=list)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    validation: Dict[str, Any] = field(default_factory=dict)
    allowed_tools: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    content: str = ""


def parse_skill_frontmatter(path: Path, content: str) -> SkillV2:
    metadata: Dict[str, Any] = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            metadata = yaml.safe_load(parts[1]) or {}
            body = parts[2].strip()

    return SkillV2(
        name=metadata.get("name", path.parent.name),
        description=metadata.get("description", ""),
        path=path,
        triggers=metadata.get("triggers", []),
        examples=metadata.get("examples", []),
        inputs=metadata.get("inputs", {}),
        outputs=metadata.get("outputs", {}),
        validation=metadata.get("validation", {}),
        allowed_tools=metadata.get("allowed-tools", []),
        metadata=metadata.get("metadata", {}),
        content=body,
    )


class SkillRegistry:
    def __init__(self, skills_dir: Path):
        self.skills_dir = Path(skills_dir).expanduser()
        self.catalog: Dict[str, SkillV2] = {}
        self._load_all()

    def _load_all(self) -> None:
        if not self.skills_dir.exists():
            return
        for category_dir in sorted(self.skills_dir.iterdir()):
            if not category_dir.is_dir():
                continue
            for skill_dir in sorted(category_dir.iterdir()):
                if not skill_dir.is_dir():
                    continue
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    skill = parse_skill_frontmatter(
                        skill_file, skill_file.read_text(encoding="utf-8")
                    )
                    self.catalog[f"{category_dir.name}/{skill_dir.name}"] = skill

    def get(self, key: str) -> Optional[SkillV2]:
        return self.catalog.get(key)

    def find_by_trigger(self, query: str) -> List[SkillV2]:
        query_lower = query.lower()
        results = []
        for skill in self.catalog.values():
            for trigger in skill.triggers:
                if trigger.lower() in query_lower:
                    results.append(skill)
                    break
        return results
