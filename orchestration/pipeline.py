"""RAG 流水线：检索 -> 单次大模型问答（引用摘录不调用 LLM）。"""

from __future__ import annotations

from collections.abc import Iterator

from config.settings import Settings, get_settings
from core.interfaces.llm import AbstractLLMService
from core.interfaces.retriever import AbstractRetriever
from core.llm.factory import create_llm_service
from core.retrievers.factory import create_retriever
from core.retrieval.relevance import filter_relevant_citations, should_skip_retrieval
from core.services.citation_preview import build_citation_summaries
from core.services.qa_service import QAService
from domain.schemas import PreparedQuery, QueryRequest, QueryResult


class QAPipeline:
    def __init__(
        self,
        retriever: AbstractRetriever | None = None,
        llm: AbstractLLMService | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._retriever = retriever or create_retriever()
        self._llm = llm or create_llm_service(self._settings)
        self._qa = QAService(self._llm)

    def prepare(self, request: QueryRequest) -> PreparedQuery:
        history = request.history
        if should_skip_retrieval(request.question, history):
            citations = []
        else:
            raw = self._retriever.retrieve(
                request.question,
                top_k=request.top_k or self._settings.retrieval_top_k_default,
            )
            citations = filter_relevant_citations(
                request.question, raw, history=history
            )

        summaries = build_citation_summaries(citations)
        llm_messages, fallback = self._qa.prepare(
            request.question, citations, history=history
        )
        return PreparedQuery(
            question=request.question,
            citations=citations,
            summaries=summaries,
            llm_messages=llm_messages,
            fallback_answer=fallback,
        )

    def stream_answer(self, prepared: PreparedQuery) -> Iterator[str]:
        if prepared.fallback_answer is not None:
            yield prepared.fallback_answer
            return
        assert prepared.llm_messages is not None
        yield from self._qa.stream_answer(prepared.llm_messages)

    def run(self, request: QueryRequest) -> QueryResult:
        prepared = self.prepare(request)
        answer = "".join(self.stream_answer(prepared))
        return QueryResult(
            question=prepared.question,
            answer=answer,
            citations=prepared.citations,
            summaries=prepared.summaries,
        )
