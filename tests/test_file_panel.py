import os
import tempfile
import tkinter as tk
import pytest
from windows.file_panel import FilePanel


@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


def test_file_panel_lists_files(root):
    with tempfile.TemporaryDirectory() as tmpdir:
        open(os.path.join(tmpdir, "test.docx"), "w").close()
        panel = FilePanel(root, root_path=tmpdir)
        items = panel.get_items()
        assert any("test.docx" in item for item in items)
