# tests/test_quick_actions.py
import tkinter as tk
import pytest
from windows.quick_actions import QuickActionsPanel


@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


def test_quick_actions_emits_callback(root):
    clicked = []
    panel = QuickActionsPanel(root, on_action=lambda action: clicked.append(action))
    panel._buttons["curriculum"].invoke()
    assert clicked == ["curriculum"]
