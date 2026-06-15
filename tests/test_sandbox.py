import tempfile
from pathlib import Path

from core.sandbox import Sandbox


def test_sandbox_allows_project_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = Sandbox(tmpdir)
        assert sandbox.is_allowed(Path(tmpdir) / "file.docx") is True


def test_sandbox_rejects_parent_escape():
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = Sandbox(tmpdir)
        assert sandbox.is_allowed(Path(tmpdir).parent / "outside.docx") is False
