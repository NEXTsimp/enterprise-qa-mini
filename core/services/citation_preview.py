"""引用摘录 — 从检索片段生成展示用 Markdown（不调用大模型）。"""

from __future__ import annotations

from domain.schemas import RetrievedChunk, SummaryOutput


def build_citation_summaries(citations: list[RetrievedChunk]) -> list[SummaryOutput]:
    summaries: list[SummaryOutput] = []
    for c in citations:
        ch = c.chunk
        excerpt = ch.content.strip()
        if len(excerpt) > 320:
            excerpt = excerpt[:320] + "…"
        md = f"**{ch.title}**\n\n{excerpt}\n\n*摘自知识库原文。*"
        summaries.append(SummaryOutput(raw_markdown=md))
    return summaries
