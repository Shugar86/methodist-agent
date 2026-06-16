import tempfile
from pathlib import Path

from core.skill_validator import SkillValidator


def _write_skill(tmpdir: str, category: str, skill_dir_name: str, content: str) -> Path:
    skill_dir = Path(tmpdir) / category / skill_dir_name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
    return skill_dir


def test_validator_rejects_missing_description():
    with tempfile.TemporaryDirectory() as tmpdir:
        _write_skill(
            tmpdir,
            "curriculum",
            "bad-skill",
            "---\nname: bad-skill\n---\n\nBody.\n",
        )
        validator = SkillValidator(tmpdir)
        errors = validator.validate_all()
        assert any("description" in err.lower() for err in errors)


def test_validator_rejects_missing_name():
    with tempfile.TemporaryDirectory() as tmpdir:
        _write_skill(
            tmpdir,
            "curriculum",
            "bad-skill",
            "---\nname: \"\"\ndescription: A skill with no name.\n---\n\nBody.\n",
        )
        validator = SkillValidator(tmpdir)
        errors = validator.validate_all()
        assert any("missing name" in err.lower() for err in errors)
        assert not any("invalid name" in err.lower() for err in errors)


def test_validator_rejects_invalid_name_with_uppercase():
    with tempfile.TemporaryDirectory() as tmpdir:
        _write_skill(
            tmpdir,
            "curriculum",
            "bad-skill",
            "---\nname: BadSkill\ndescription: Uppercase letters are not allowed.\n---\n\nBody.\n",
        )
        validator = SkillValidator(tmpdir)
        errors = validator.validate_all()
        assert any("invalid name" in err.lower() for err in errors)


def test_validator_rejects_invalid_name_with_spaces():
    with tempfile.TemporaryDirectory() as tmpdir:
        _write_skill(
            tmpdir,
            "curriculum",
            "bad-skill",
            "---\nname: bad skill\ndescription: Spaces are not allowed.\n---\n\nBody.\n",
        )
        validator = SkillValidator(tmpdir)
        errors = validator.validate_all()
        assert any("invalid name" in err.lower() for err in errors)


def test_validator_rejects_description_too_long():
    with tempfile.TemporaryDirectory() as tmpdir:
        _write_skill(
            tmpdir,
            "curriculum",
            "bad-skill",
            "---\nname: bad-skill\ndescription: " + "x" * 1025 + "\n---\n\nBody.\n",
        )
        validator = SkillValidator(tmpdir)
        errors = validator.validate_all()
        assert any("description too long" in err.lower() for err in errors)


def test_validator_rejects_duplicate_names():
    with tempfile.TemporaryDirectory() as tmpdir:
        _write_skill(
            tmpdir,
            "category-a",
            "skill-a",
            "---\nname: shared-name\ndescription: First skill.\n---\n\nBody.\n",
        )
        _write_skill(
            tmpdir,
            "category-b",
            "skill-b",
            "---\nname: shared-name\ndescription: Second skill.\n---\n\nBody.\n",
        )
        validator = SkillValidator(tmpdir)
        errors = validator.validate_all()
        assert any("duplicate name" in err.lower() for err in errors)


def test_validator_accepts_valid_skill():
    with tempfile.TemporaryDirectory() as tmpdir:
        _write_skill(
            tmpdir,
            "curriculum",
            "good-skill",
            "---\nname: good-skill\ndescription: A valid skill description.\n---\n\nBody.\n",
        )
        validator = SkillValidator(tmpdir)
        errors = validator.validate_all()
        assert errors == []


def test_sample_skills_pass_validation():
    from pathlib import Path
    from core.skill_validator import SkillValidator

    skills_dir = Path(__file__).parent.parent / "skills"
    validator = SkillValidator(skills_dir)
    errors = validator.validate_all()
    assert errors == [], f"Skill validation errors: {errors}"
