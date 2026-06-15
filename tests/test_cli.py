"""CLI integration tests for Methodist Agent."""

import shutil
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from core.config import Config, AgentConfig, DocumentsConfig, SkillsConfig
from core.environment_check import EnvironmentReport, CheckItem
from src.main import app

runner = CliRunner()

PROJECT_ROOT = Path(__file__).parent.parent


def _make_config(tmp_path: Path) -> Config:
    """Build a config that keeps all file operations under tmp_path."""
    return Config(
        agent=AgentConfig(data_dir=str(tmp_path / ".methodist-agent")),
        documents=DocumentsConfig(
            default_template_path=str(tmp_path / ".methodist-agent" / "templates"),
            output_path=str(tmp_path / ".methodist-agent" / "output"),
        ),
        skills=SkillsConfig(repository=str(tmp_path / ".methodist-agent" / "skills")),
    )


def test_init_check_all_good(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    report = EnvironmentReport(
        items=[
            CheckItem(name="A", available=True, message="ok"),
        ]
    )
    with patch("src.main.run_environment_check", return_value=report):
        result = runner.invoke(app, ["init", "--check"])
    assert result.exit_code == 0
    assert "Проверка окружения" in result.output


def test_init_check_not_good(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    report = EnvironmentReport(
        items=[
            CheckItem(
                name="A",
                available=False,
                message="missing",
                recommendation="install A",
            ),
        ]
    )
    with patch("src.main.run_environment_check", return_value=report):
        result = runner.invoke(app, ["init", "--check"])
    assert result.exit_code == 1
    assert "Проверка окружения" in result.output


def test_init_onboarding(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    config = _make_config(tmp_path)
    report = EnvironmentReport(
        items=[CheckItem(name="A", available=True, message="ok")]
    )
    with patch("src.main.load_config", return_value=config):
        with patch("src.main.run_environment_check", return_value=report):
            result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Добро пожаловать" in result.output


def test_create_curriculum(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    config = _make_config(tmp_path)

    template_dir = tmp_path / "templates"
    output_dir = tmp_path / "output"
    template_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    project_curriculum = PROJECT_ROOT / "templates" / "curriculum"
    if project_curriculum.exists():
        shutil.copytree(
            project_curriculum, template_dir / "curriculum", dirs_exist_ok=True
        )

    import agents.document_specialist as ds

    monkeypatch.setattr(ds, "TEMPLATES_DIR", template_dir)
    monkeypatch.setattr(ds, "OUTPUT_DIR", output_dir)

    with patch("src.main.load_config", return_value=config):
        result = runner.invoke(
            app,
            ["create", "curriculum", "--subject", "Базы данных", "--hours", "144"],
        )
    assert result.exit_code == 0
    assert "Документ готов" in result.output
