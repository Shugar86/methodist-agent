from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

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
