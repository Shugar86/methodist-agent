import tkinter as tk
import pytest
from windows.chat_panel import ChatPanel


@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


def test_chat_panel_adds_message(root):
    panel = ChatPanel(root)
    panel.add_message("user", "Привет")
    assert "Привет" in panel.get_text()
    assert "user" in panel.get_text()
