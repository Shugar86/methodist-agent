"""CLI integration tests for Methodist Agent."""

import shutil
from pathlib import Path

from typer.testing import CliRunner

from src.main import app

runner = CliRunner()

PROJECT_ROOT = Path(__file__).parent.parent


def test_init_check():
    result = runner.invoke(app, ["init", "--check"])
    assert result.exit_code in (0, 1)
    assert "Проверка окружения" in result.output


def test_init_onboarding():
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Добро пожаловать" in result.output


def test_create_curriculum(tmp_path, monkeypatch):
    template_dir = tmp_path / "templates"
    output_dir = tmp_path / "output"
    shutil.copytree(PROJECT_ROOT / "templates" / "curriculum", template_dir / "curriculum")

    import agents.document_specialist as ds

    monkeypatch.setattr(ds, "TEMPLATES_DIR", template_dir)
    monkeypatch.setattr(ds, "OUTPUT_DIR", output_dir)

    result = runner.invoke(
        app, ["create", "curriculum", "--subject", "Test Subject", "--hours", "10"]
    )
    assert result.exit_code == 0
    assert "Документ готов" in result.output
