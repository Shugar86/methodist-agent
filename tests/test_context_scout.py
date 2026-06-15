from pathlib import Path
import tempfile

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
