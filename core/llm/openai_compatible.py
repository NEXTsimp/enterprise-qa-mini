"""OpenAI 兼容 API 实现 — 同时覆盖 OpenAI / DeepSeek / DashScope。"""

from __future__ import annotations

from collections.abc import Iterator

from openai import OpenAI

from config.settings import Settings
from core.interfaces.llm import AbstractLLMService, LLMMessage


class OpenAICompatibleLLM(AbstractLLMService):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = OpenAI(
            api_key=settings.llm_api_key or "sk-placeholder",
            base_url=settings.llm_base_url,
        )

    def chat(self, messages: list[LLMMessage], **kwargs) -> str:
        response = self._client.chat.completions.create(
            model=kwargs.get("model", self._settings.llm_model),
            messages=[m.model_dump() for m in messages],
            temperature=kwargs.get("temperature", self._settings.llm_temperature),
            max_tokens=kwargs.get("max_tokens", self._settings.llm_max_tokens),
        )
        return response.choices[0].message.content or ""

    def chat_stream(self, messages: list[LLMMessage], **kwargs) -> Iterator[str]:
        stream = self._client.chat.completions.create(
            model=kwargs.get("model", self._settings.llm_model),
            messages=[m.model_dump() for m in messages],
            temperature=kwargs.get("temperature", self._settings.llm_temperature),
            max_tokens=kwargs.get("max_tokens", self._settings.llm_max_tokens),
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    def health_check(self) -> bool:
        return bool(self._settings.llm_api_key)
