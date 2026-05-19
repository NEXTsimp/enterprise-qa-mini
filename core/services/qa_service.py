"""问答领域服务 — 基于检索上下文生成受限回答。"""

from __future__ import annotations

from collections.abc import Iterator

from config.prompts import (
    QA_CONVERSATION_SYSTEM_PROMPT,
    QA_SYSTEM_PROMPT,
    QA_USER_TEMPLATE,
)
from core.interfaces.llm import AbstractLLMService, LLMMessage
from core.retrieval.relevance import should_skip_retrieval
from core.services.fallback_reply import build_fallback_reply
from domain.schemas import RetrievedChunk


class QAService:
    def __init__(self, llm: AbstractLLMService) -> None:
        self._llm = llm

    def prepare(
        self,
        question: str,
        citations: list[RetrievedChunk],
        history: list[LLMMessage] | None = None,
    ) -> tuple[list[LLMMessage] | None, str | None]:
        q = question.strip()
        hist = list(history or [])

        if not citations:
            if should_skip_retrieval(q, hist):
                return (
                    [
                        LLMMessage(role="system", content=QA_CONVERSATION_SYSTEM_PROMPT),
                        *hist,
                        LLMMessage(role="user", content=q),
                    ],
                    None,
                )
            return None, build_fallback_reply(q)

        user_content = QA_USER_TEMPLATE.format(
            title=citations[0].chunk.title,
            content=citations[0].chunk.content,
            question=q,
        )
        return (
            [
                LLMMessage(role="system", content=QA_SYSTEM_PROMPT),
                *hist,
                LLMMessage(role="user", content=user_content),
            ],
            None,
        )

    def answer(
        self,
        question: str,
        citations: list[RetrievedChunk],
        history: list[LLMMessage] | None = None,
    ) -> str:
        messages, fallback = self.prepare(question, citations, history)
        if fallback is not None:
            return fallback
        assert messages is not None
        return self._llm.chat(messages)

    def stream_answer(self, messages: list[LLMMessage]) -> Iterator[str]:
        yield from self._llm.chat_stream(messages)
