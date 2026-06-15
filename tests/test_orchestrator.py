from unittest.mock import MagicMock

from core.context_scout import ContextItem
from core.orchestrator import Orchestrator


def test_orchestrator_uses_context_scout():
    config = MagicMock()
    config.approval.enabled = False
    model_router = MagicMock()
    model_router.chat.return_value.content = "[]"
    context_manager = MagicMock()
    context_manager._current_session = None
    scout = MagicMock()
    scout.find_relevant.return_value = [
        ContextItem(
            key="curriculum/create-rpd",
            source="skill",
            content="create-rpd: Создаёт РПД.",
            score=10,
        )
    ]

    orch = Orchestrator(config, model_router, context_manager, context_scout=scout)
    orch.create_plan("создай рабочую программу")
    scout.find_relevant.assert_called_once()
    sent_messages = model_router.chat.call_args[0][0]
    assert "create-rpd: Создаёт РПД." in sent_messages[0].content
