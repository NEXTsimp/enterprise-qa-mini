"""LLM 服务抽象 — 可替换 OpenAI / DeepSeek / DashScope / 本地模型。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

from pydantic import BaseModel, Field


class LLMMessage(BaseModel):
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str


class AbstractLLMService(ABC):
    @abstractmethod
    def chat(self, messages: list[LLMMessage], **kwargs) -> str:
        """多轮对话补全，返回 assistant 文本。"""

    def chat_stream(self, messages: list[LLMMessage], **kwargs) -> Iterator[str]:
        """流式对话补全；默认一次性 yield 完整回复。"""
        yield self.chat(messages, **kwargs)

    @abstractmethod
    def health_check(self) -> bool:
        """API 密钥、端点是否可用。"""
