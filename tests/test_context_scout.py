from pathlib import Path
import tempfile

import pytest

from core.context_scout import ContextScout
from core.skill_registry import SkillRegistry


def test_context_scout_finds_skill_by_trigger():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "curriculum" / "create-rpd"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: create-rpd\ndescription: Создаёт РПД.\ntriggers:\n  - рабочую программу\n---\n\nИнструкции.\n",
            encoding="utf-8",
        )
        registry = SkillRegistry(tmpdir)
        scout = ContextScout(skill_registry=registry)
        results = scout.find_relevant("создай рабочую программу по математике")
        assert any(item.key == "curriculum/create-rpd" for item in results)


def test_context_scout_finds_skill_by_description():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "format" / "format-table"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: format-table\ndescription: Форматирует таблицу\ntriggers: []\n---\n\nИнструкции.\n",
            encoding="utf-8",
        )
        registry = SkillRegistry(tmpdir)
        scout = ContextScout(skill_registry=registry)
        results = scout.find_relevant("как форматирует таблицу в рпд")
        assert any(item.key == "format/format-table" for item in results)


def test_context_scout_trigger_scores_higher_than_description():
    with tempfile.TemporaryDirectory() as tmpdir:
        trigger_dir = Path(tmpdir) / "search" / "find-skill"
        trigger_dir.mkdir(parents=True)
        (trigger_dir / "SKILL.md").write_text(
            "---\nname: find-skill\ndescription: Ищет ресурсы.\ntriggers:\n  - поиск\n---\n\nИнструкции.\n",
            encoding="utf-8",
        )

        desc_dir = Path(tmpdir) / "desc" / "describe-skill"
        desc_dir.mkdir(parents=True)
        (desc_dir / "SKILL.md").write_text(
            "---\nname: describe-skill\ndescription: Описывает поисковый запрос.\ntriggers: []\n---\n\nИнструкции.\n",
            encoding="utf-8",
        )

        registry = SkillRegistry(tmpdir)
        scout = ContextScout(skill_registry=registry)
        results = scout.find_relevant("поисковый запрос")
        assert [item.key for item in results] == ["search/find-skill", "desc/describe-skill"]


def test_context_scout_top_k_limits_results():
    with tempfile.TemporaryDirectory() as tmpdir:
        for category, key, trigger in [
            ("a", "skill-one", "alpha"),
            ("b", "skill-two", "beta"),
            ("c", "skill-three", "gamma"),
        ]:
            skill_dir = Path(tmpdir) / category / key
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {key}\ndescription: Навык.\ntriggers:\n  - {trigger}\n---\n\nИнструкции.\n",
                encoding="utf-8",
            )

        registry = SkillRegistry(tmpdir)
        scout = ContextScout(skill_registry=registry)
        results = scout.find_relevant("alpha beta gamma", top_k=2)
        assert len(results) == 2
        assert results[0].key == "a/skill-one"
        assert results[1].key == "b/skill-two"


def test_context_scout_no_matches_returns_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "misc" / "orphan"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: orphan\ndescription: Нет совпадений.\ntriggers: []\n---\n\nИнструкции.\n",
            encoding="utf-8",
        )
        registry = SkillRegistry(tmpdir)
        scout = ContextScout(skill_registry=registry)
        assert scout.find_relevant("абракадабра тест") == []


@pytest.mark.parametrize("query", ["", "   ", "\t\n"])
def test_context_scout_empty_or_whitespace_query_returns_empty(query):
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "misc" / "empty-test"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: empty-test\ndescription: Проверка пустого запроса.\ntriggers:\n  - проверка\n---\n\nИнструкции.\n",
            encoding="utf-8",
        )
        registry = SkillRegistry(tmpdir)
        scout = ContextScout(skill_registry=registry)
        assert scout.find_relevant(query) == []
