from dataclasses import dataclass
from typing import List, Optional

from core.skill_registry import SkillRegistry


@dataclass
class ContextItem:
    key: str
    source: str  # "skill", "template", "context_file", "session"
    content: str
    score: int


class ContextScout:
    def __init__(self, skill_registry: Optional[SkillRegistry] = None):
        self.skill_registry = skill_registry

    def find_relevant(self, query: str, top_k: int = 5) -> List[ContextItem]:
        if not query or not query.strip():
            return []
        query_lower = query.lower()
        scored: List[ContextItem] = []

        if self.skill_registry:
            for key, skill in self.skill_registry.catalog.items():
                score = 0
                for trigger in skill.triggers:
                    if trigger.lower() in query_lower:
                        score += 10
                if skill.description.lower() in query_lower:
                    score += 5
                if query_lower in skill.description.lower():
                    score += 3
                if score > 0:
                    scored.append(
                        ContextItem(
                            key=key,
                            source="skill",
                            content=f"{skill.name}: {skill.description}",
                            score=score,
                        )
                    )

        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_k]
