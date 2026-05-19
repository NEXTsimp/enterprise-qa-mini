"""检索器工厂 — 当前仅注册 BM25 实现。"""

from __future__ import annotations

from config.settings import Settings, get_settings
from core.interfaces.retriever import AbstractRetriever
from core.retrievers.bm25_retriever import BM25Retriever


def create_retriever(settings: Settings | None = None) -> AbstractRetriever:
    cfg = settings or get_settings()
    if cfg.retriever_backend != "bm25":
        raise ValueError(
            f"不支持的 retriever_backend={cfg.retriever_backend!r}，"
            "当前版本仅支持 bm25"
        )
    return BM25Retriever()
