"""本地大模型 — Ollama 等 OpenAI 兼容端点（默认 http://localhost:11434）。"""

from __future__ import annotations

from collections.abc import Iterator

from openai import OpenAI

from core.interfaces.llm import AbstractLLMService, LLMMessage


def _normalize_base_url(endpoint: str) -> str:
    base = endpoint.strip().rstrip("/")
    if base.endswith("/v1"):
        return base
    return f"{base}/v1"


class LocalLLMService(AbstractLLMService):
    def __init__(
        self,
        endpoint: str = "http://localhost:11434",
        model: str = "llama3.2",
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> None:
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._client = OpenAI(
            api_key="ollama",
            base_url=_normalize_base_url(endpoint),
        )

    def chat(self, messages: list[LLMMessage], **kwargs) -> str:
        response = self._client.chat.completions.create(
            model=kwargs.get("model", self._model),
            messages=[m.model_dump() for m in messages],
            temperature=kwargs.get("temperature", self._temperature),
            max_tokens=kwargs.get("max_tokens", self._max_tokens),
        )
        return response.choices[0].message.content or ""

    def chat_stream(self, messages: list[LLMMessage], **kwargs) -> Iterator[str]:
        stream = self._client.chat.completions.create(
            model=kwargs.get("model", self._model),
            messages=[m.model_dump() for m in messages],
            temperature=kwargs.get("temperature", self._temperature),
            max_tokens=kwargs.get("max_tokens", self._max_tokens),
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    def health_check(self) -> bool:
        try:
            self._client.models.list()
            return True
        except Exception:
            return False
