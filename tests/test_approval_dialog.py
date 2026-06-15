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
    dialog._approve()
    assert dialog.result is True
