import tkinter as tk

import pytest
from core.config import AgentConfig, Config
from core.document_environment import DocumentEnvironment
from core.sandbox import Sandbox
from drivers.com_driver import COMDriver
from drivers.native_driver import NativeDriver
from windows.workspace import MethodistWorkspace


@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


def test_workspace_creates_panels(root, tmp_path):
    config = Config(agent=AgentConfig(data_dir=str(tmp_path)))
    ws = MethodistWorkspace(root, config=config)
    assert ws.chat_panel is not None
    assert ws.quick_actions is not None
    assert ws.file_panel is not None


def test_workspace_has_document_environment(tmp_path):
    config = Config()
    ws = MethodistWorkspace(config=config)
    assert isinstance(ws.document_environment, DocumentEnvironment)
    assert isinstance(ws.document_environment.sandbox, Sandbox)
    assert any(isinstance(d, COMDriver) for d in ws.document_environment.drivers)
    assert any(isinstance(d, NativeDriver) for d in ws.document_environment.drivers)
    assert ws.document_environment.event_bus is ws.event_bus
    ws.root.destroy()
