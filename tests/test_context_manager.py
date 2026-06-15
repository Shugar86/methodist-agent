# tests/test_context_manager.py
from unittest.mock import MagicMock
from core.context_manager import ContextManager, Skill


def test_context_manager_uses_skill_registry(tmp_path):
    config = MagicMock()
    config.skills.repository = str(tmp_path)
    config.skills.auto_load = True
    cm = ContextManager(config)
    assert hasattr(cm, "skill_registry")


def test_context_manager_delegates_to_skill_registry(tmp_path):
    skill_dir = tmp_path / "test-category" / "test-skill"
    skill_dir.mkdir(parents=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        "---\nname: test-skill\ntriggers:\n  - test query\n---\nSkill body content.\n",
        encoding="utf-8",
    )

    config = MagicMock()
    config.skills.repository = str(tmp_path)
    config.skills.auto_load = True
    cm = ContextManager(config)

    assert hasattr(cm, "_context_scout")

    all_skills = cm.get_all_skills()
    assert "test-category/test-skill" in all_skills
    skill = all_skills["test-category/test-skill"]
    assert isinstance(skill, Skill)
    assert skill.category == "test-category"
    assert skill.name == "test-skill"
    assert skill.triggers == ["test query"]

    found = cm.get_skill("test-category", "test-skill")
    assert isinstance(found, Skill)
    assert found.name == "test-skill"

    matches = cm.find_skills("test query")
    assert any(s.name == "test-skill" for s in matches)
