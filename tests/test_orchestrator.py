from unittest.mock import MagicMock

from core.orchestrator import Orchestrator


def test_orchestrator_uses_context_scout():
    config = MagicMock()
    config.approval.enabled = False
    model_router = MagicMock()
    model_router.chat.return_value.content = "[]"
    context_manager = MagicMock()
    context_manager._current_session = None
    scout = MagicMock()
    scout.find_relevant.return_value = []

    orch = Orchestrator(config, model_router, context_manager, context_scout=scout)
    orch.create_plan("создай рабочую программу")
    scout.find_relevant.assert_called_once()
