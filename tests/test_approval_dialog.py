import tkinter as tk
import pytest
from windows.approval_dialog import ApprovalDialog


@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


def test_approval_dialog_returns_approved(root):
    dialog = ApprovalDialog(root, plan_text="1. Создать документ")
    # Simulate approval without blocking.
    dialog._approved = True
    dialog._close()
    assert dialog.result is True
