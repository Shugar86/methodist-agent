"""
Model Router - manages LLM providers and handles API calls.
Supports OpenAI, Anthropic, Ollama, and other providers.
"""

import os
from typing import Optional, Dict, Any, List, Iterator
from dataclasses import dataclass

from core.config import Config, ModelConfig


@dataclass
class Message:
    """A chat message."""

    role: str  # system, user, assistant, tool
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None


@dataclass
class ChatResponse:
    """Response from LLM."""

    content: str
    model: str
    usage: Dict[str, int]
    raw_response: Any = None


class ModelRouter:
    """Routes requests to appropriate LLM provider."""

    def __init__(self, config: Config):
        self.config = config
        self.current_model = "primary"
        self._clients = {}

    def _get_client(self, model_name: str):
        """Get or create client for specified model."""
        if model_name in self._clients:
            return self._clients[model_name]

        model_config = self.config.models.get(model_name)
        if not model_config:
            raise ValueError(f"Unknown model: {model_name}")

        client = self._create_client(model_config)
        self._clients[model_name] = client
        return client

    def _create_client(self, model_config: ModelConfig):
        """Create API client based on provider."""
        provider = model_config.provider.lower()

        if provider == "openai":
            try:
                import openai

                api_key = model_config.api_key or os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OpenAI API key not found")
                return openai.OpenAI(api_key=api_key, base_url=model_config.api_base)
            except ImportError:
                raise ImportError("Install openai package: pip install openai")

        elif provider == "anthropic":
            try:
                import anthropic

                api_key = model_config.api_key or os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("Anthropic API key not found")
                return anthropic.Anthropic(api_key=api_key, base_url=model_config.api_base)
            except ImportError:
                raise ImportError("Install anthropic package: pip install anthropic")

        elif provider == "ollama":
            try:
                import openai

                base_url = model_config.api_base or "http://localhost:11434/v1"
                return openai.OpenAI(base_url=base_url, api_key="ollama")
            except ImportError:
                raise ImportError("Install openai package for Ollama compatibility")

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def chat(
        self,
        messages: List[Message],
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        stream: bool = False,
    ) -> ChatResponse | Iterator[Any]:
        """Send chat request to LLM."""
        model_name = model_name or self.current_model
        model_config = self.config.models.get(model_name)
        if not model_config:
            # Fallback to primary
            model_name = "primary"
            model_config = self.config.models.get("primary")

        client = self._get_client(model_name)
        provider = model_config.provider.lower()

        try:
            if provider in ["openai", "ollama"]:
                return self._chat_openai(
                    client, messages, model_config, temperature, max_tokens, tools, stream
                )
            elif provider == "anthropic":
                return self._chat_anthropic(
                    client, messages, model_config, temperature, max_tokens, tools, stream
                )
            else:
                raise ValueError(f"Chat not implemented for provider: {provider}")
        except Exception as e:
            # Try fallback model
            if model_name != "fallback" and "fallback" in self.config.models:
                print(f"Primary model failed ({e}), trying fallback...")
                return self.chat(messages, "fallback", temperature, max_tokens, tools, stream)
            raise

    def _chat_openai(
        self, client, messages, model_config, temperature, max_tokens, tools, stream
    ) -> ChatResponse | Iterator[Any]:
        """Chat using OpenAI-compatible API."""
        formatted_messages = []
        for msg in messages:
            m = {"role": msg.role, "content": msg.content}
            if msg.name:
                m["name"] = msg.name
            formatted_messages.append(m)

        kwargs = {
            "model": model_config.model,
            "messages": formatted_messages,
            "temperature": temperature or model_config.temperature,
            "max_tokens": max_tokens or model_config.max_tokens,
        }
        if tools:
            kwargs["tools"] = tools

        if stream:
            kwargs["stream"] = True
            return client.chat.completions.create(**kwargs)

        response = client.chat.completions.create(**kwargs)

        return ChatResponse(
            content=response.choices[0].message.content or "",
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            raw_response=response,
        )

    def _chat_anthropic(
        self, client, messages, model_config, temperature, max_tokens, tools, stream
    ) -> ChatResponse | Iterator[Any]:
        """Chat using Anthropic API."""
        system_msg = None
        formatted_messages = []

        for msg in messages:
            if msg.role == "system":
                system_msg = msg.content
            else:
                formatted_messages.append({"role": msg.role, "content": msg.content})

        kwargs = {
            "model": model_config.model,
            "messages": formatted_messages,
            "temperature": temperature or model_config.temperature,
            "max_tokens": max_tokens or model_config.max_tokens,
        }
        if system_msg:
            kwargs["system"] = system_msg
        if tools:
            kwargs["tools"] = tools

        if stream:
            kwargs["stream"] = True
            return client.messages.create(**kwargs)

        response = client.messages.create(**kwargs)

        return ChatResponse(
            content=response.content[0].text if response.content else "",
            model=response.model,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            },
            raw_response=response,
        )

    def get_available_models(self) -> List[str]:
        """Get list of configured model names."""
        return list(self.config.models.keys())

    def switch_model(self, model_name: str) -> None:
        """Switch to specified model."""
        if model_name not in self.config.models:
            raise ValueError(f"Model {model_name} not configured")
        self.current_model = model_name
