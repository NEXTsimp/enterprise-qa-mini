"""检索器单元测试骨架。"""

from core.retrievers.bm25_retriever import BM25Retriever


def test_bm25_retrieve_annual_leave():
    retriever = BM25Retriever()
    hits = retriever.retrieve("年假可以结转吗", top_k=1)
    assert len(hits) == 1
    assert "年假" in hits[0].chunk.title or "年假" in hits[0].chunk.content
