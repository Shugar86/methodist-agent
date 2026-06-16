# tests/test_context_manager.py
from unittest.mock import MagicMock
from core.context_manager import ContextManager, Skill


def _build_config(tmp_path, *, auto_load: bool = True) -> MagicMock:
    config = MagicMock()
    config.skills.repository = str(tmp_path)
    config.skills.auto_load = auto_load
    return config


def test_context_manager_uses_skill_registry(tmp_path):
    config = _build_config(tmp_path, auto_load=True)
    cm = ContextManager(config)
    assert cm.skill_registry is not None


def test_context_manager_delegates_to_skill_registry(tmp_path):
    skill_dir = tmp_path / "test-category" / "test-skill"
    skill_dir.mkdir(parents=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        "---\nname: test-skill\ntriggers:\n  - test query\n---\nSkill body content.\n",
        encoding="utf-8",
    )

    config = _build_config(tmp_path, auto_load=True)
    cm = ContextManager(config)

    assert cm._context_scout is not None

    all_skills = cm.get_all_skills()
    assert "test-category/test-skill" in all_skills
    skill = all_skills["test-category/test-skill"]
    assert isinstance(skill, Skill)
    assert skill.category == "test-category"
    assert skill.name == "test-skill"
    assert skill.triggers == ["test query"]
    assert skill.path.is_dir()
    assert skill.content.startswith("---")

    found = cm.get_skill("test-category", "test-skill")
    assert isinstance(found, Skill)
    assert found.name == "test-skill"
    assert found.path.is_dir()
    assert found.content.startswith("---")

    matches = cm.find_skills("test query")
    assert any(s.name == "test-skill" for s in matches)


def test_find_skills_returns_empty_for_unknown_query(tmp_path):
    skill_dir = tmp_path / "test-category" / "test-skill"
    skill_dir.mkdir(parents=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        "---\nname: test-skill\ndescription: A test skill\ntriggers:\n  - test query\n---\nSkill body content.\n",
        encoding="utf-8",
    )

    config = _build_config(tmp_path, auto_load=True)
    cm = ContextManager(config)

    assert cm.find_skills("несуществующий запрос") == []


def test_get_skill_returns_none_for_missing_skill(tmp_path):
    config = _build_config(tmp_path, auto_load=True)
    cm = ContextManager(config)

    assert cm.get_skill("missing", "missing") is None


def test_skills_disabled_when_auto_load_false(tmp_path):
    config = _build_config(tmp_path, auto_load=False)
    cm = ContextManager(config)

    assert cm.skill_registry is None
    assert cm._context_scout is None
    assert cm.get_all_skills() == {}
    assert cm.get_skill("cat", "name") is None
    assert cm.find_skills("anything") == []
