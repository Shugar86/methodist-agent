# tests/test_context_manager.py
from unittest.mock import MagicMock
from core.context_manager import ContextManager


def test_context_manager_uses_skill_registry(tmp_path):
    config = MagicMock()
    config.skills.repository = str(tmp_path)
    config.skills.auto_load = True
    cm = ContextManager(config)
    assert hasattr(cm, "skill_registry")
