"""Smoke test for MethodistWorkspace initialization."""

from unittest.mock import patch

from windows.workspace import MethodistWorkspace


@patch("windows.workspace.MethodistWorkspace._build_ui")
def test_workspace_smoke_init(mock_build_ui):
    ws = MethodistWorkspace()
    try:
        assert ws.root.title() == "Методист-Агент"
    finally:
        ws.root.destroy()
