from pathlib import Path
import tempfile

from core.skill_validator import SkillValidator


def test_validator_rejects_missing_description():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "curriculum" / "bad-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: bad-skill\n---\n\nBody.\n", encoding="utf-8"
        )
        validator = SkillValidator(tmpdir)
        errors = validator.validate_all()
        assert any("description" in err.lower() for err in errors)
