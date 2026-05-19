"""Pydantic 数据契约。"""

from __future__ import annotations

from pydantic import BaseModel, Field

from core.interfaces.llm import LLMMessage


class DocumentChunk(BaseModel):
    chunk_id: str
    doc_id: str
    title: str
    content: str
    metadata: dict[str, str] = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    chunk: DocumentChunk
    score: float
    rank: int = 1


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=1, ge=1, le=10)
    history: list[LLMMessage] = Field(default_factory=list)


class SummaryOutput(BaseModel):
    """引用区展示的摘录 Markdown（由 citation_preview 生成，非 LLM 摘要）。"""

    raw_markdown: str = ""


class PreparedQuery(BaseModel):
    question: str
    citations: list[RetrievedChunk] = Field(default_factory=list)
    summaries: list[SummaryOutput] = Field(default_factory=list)
    llm_messages: list[LLMMessage] | None = None
    fallback_answer: str | None = None


class QueryResult(BaseModel):
    question: str
    answer: str
    citations: list[RetrievedChunk]
    summaries: list[SummaryOutput]
