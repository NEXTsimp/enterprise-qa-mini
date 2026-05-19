"""应用控制器 — UI 层唯一入口，屏蔽编排与依赖细节。"""

from __future__ import annotations

from collections.abc import Iterator

from core.interfaces.llm import LLMMessage
from domain.schemas import PreparedQuery, QueryRequest, QueryResult
from orchestration.pipeline import QAPipeline


class QAController:
    def __init__(self, pipeline: QAPipeline | None = None) -> None:
        self._pipeline = pipeline or QAPipeline()

    def prepare(
        self,
        question: str,
        top_k: int = 1,
        history: list[LLMMessage] | None = None,
    ) -> PreparedQuery:
        request = QueryRequest(
            question=question.strip(),
            top_k=top_k,
            history=history or [],
        )
        return self._pipeline.prepare(request)

    def stream_answer(self, prepared: PreparedQuery) -> Iterator[str]:
        return self._pipeline.stream_answer(prepared)

    def ask(
        self,
        question: str,
        top_k: int = 1,
        history: list[LLMMessage] | None = None,
    ) -> QueryResult:
        request = QueryRequest(
            question=question.strip(),
            top_k=top_k,
            history=history or [],
        )
        return self._pipeline.run(request)
