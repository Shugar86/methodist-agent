"""Smoke tests for DocumentSpecialist (native mode)."""

import tempfile
from pathlib import Path

from core.config import Config
from agents.document_specialist import DocumentSpecialist


def test_create_docx_native():
    """DocumentSpecialist can create a DOCX in native mode."""
    config = Config()
    agent = DocumentSpecialist(config)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test.docx"
        result = agent.create_docx(
            {
                "content": ["Заголовок", "Первый абзац", "Второй абзац"],
                "filename": output_path.name,
                "subject": "Тест",
            }
        )

        assert result["success"] is True
        assert result["mode"] == "native"
        assert Path(result["path"]).exists()
