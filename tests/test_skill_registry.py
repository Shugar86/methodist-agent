import tempfile
from pathlib import Path

from core.skill_registry import SkillRegistry, SkillV2, parse_skill_frontmatter


def test_parse_skill_frontmatter():
    content = """---
name: create-rpd
description: Создаёт рабочую программу.
triggers:
  - рабочая программа
---

# Инструкции
1. Запроси дисциплину.
"""
    skill = parse_skill_frontmatter(Path("/tmp/create-rpd/SKILL.md"), content)
    assert isinstance(skill, SkillV2)
    assert skill.name == "create-rpd"
    assert skill.description == "Создаёт рабочую программу."
    assert skill.triggers == ["рабочая программа"]


def test_skill_registry_loads_skills():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "curriculum" / "create-rpd"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: create-rpd\ndescription: Создаёт РПД.\ntriggers:\n  - рабочая программа\n---\n\nИнструкции.\n",
            encoding="utf-8",
        )
        registry = SkillRegistry(tmpdir)
        assert "curriculum/create-rpd" in registry.catalog
        assert registry.catalog["curriculum/create-rpd"].description == "Создаёт РПД."
