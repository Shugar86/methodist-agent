from pathlib import Path

from core.skill_registry import SkillV2, parse_skill_frontmatter


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
