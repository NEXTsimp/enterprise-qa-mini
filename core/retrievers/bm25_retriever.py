"""BM25 检索实现 — MVP 默认后端，无外部向量库依赖。"""

from __future__ import annotations

import re

import jieba
from rank_bm25 import BM25Okapi

from core.interfaces.retriever import AbstractRetriever
from data.mock_docs import MOCK_DOCS
from domain.schemas import DocumentChunk, RetrievedChunk


def _tokenize(text: str) -> list[str]:
    text = re.sub(r"\s+", "", text)
    return [t for t in jieba.cut_for_search(text) if t.strip()] or list(text)


class BM25Retriever(AbstractRetriever):
    def __init__(self, docs: list[dict[str, str]] | None = None) -> None:
        self._docs = docs or MOCK_DOCS
        corpus = [_tokenize(f"{d['title']} {d['content']}") for d in self._docs]
        self._bm25 = BM25Okapi(corpus)

    def retrieve(self, query: str, top_k: int = 1) -> list[RetrievedChunk]:
        if not query.strip():
            return []

        scores = self._bm25.get_scores(_tokenize(query))
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[
            :top_k
        ]

        results: list[RetrievedChunk] = []
        for rank, idx in enumerate(ranked, start=1):
            doc = self._docs[idx]
            chunk = DocumentChunk(
                chunk_id=f"{doc['id']}_0",
                doc_id=doc["id"],
                title=doc["title"],
                content=doc["content"],
            )
            results.append(
                RetrievedChunk(chunk=chunk, score=float(scores[idx]), rank=rank)
            )
        return results
    def health_check(self) -> bool:
        return len(self._docs) > 0

