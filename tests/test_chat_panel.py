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


def test_chat_panel_stream_message(root):
    panel = ChatPanel(root)
    panel.start_stream()
    panel.append_stream_chunk("Привет")
    panel.append_stream_chunk(" мир")
    panel.finish_stream()
    text = panel.get_text()
    assert "assistant:" in text
    assert text.rstrip().endswith("Привет мир")
