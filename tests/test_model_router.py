"""Tests for ModelRouter streaming support."""

from unittest.mock import patch, MagicMock

from core.model_router import ModelRouter, Message
from core.config import Config


def test_model_router_stream_returns_chunks():
    config = Config()
    router = ModelRouter(config)

    with (
        patch.object(router, "_create_client", return_value=MagicMock()) as mock_create_client,
        patch.object(router, "_chat_openai", return_value=iter(["Hello", " world"])) as mock_chat,
    ):
        chunks = list(router.chat([Message(role="user", content="Hi")], stream=True))
        mock_create_client.assert_called_once()
        mock_chat.assert_called_once()
        assert "".join(chunks) == "Hello world"


def test_model_router_stream_returns_chunks_anthropic():
    config = Config()
    router = ModelRouter(config)
    router.switch_model("fallback")
    with (
        patch.object(router, "_create_client", return_value=MagicMock()),
        patch.object(router, "_chat_anthropic", return_value=iter(["Hi", " there"])) as mock_chat,
    ):
        chunks = list(router.chat([Message(role="user", content="Hello")], stream=True))
        mock_chat.assert_called_once()
        assert "".join(chunks) == "Hi there"
