import tkinter as tk
import pytest
from windows.workspace import MethodistWorkspace


@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


def test_workspace_creates_panels(root):
    ws = MethodistWorkspace(root)
    assert ws.chat_panel is not None
    assert ws.quick_actions is not None
    assert ws.file_panel is not None
