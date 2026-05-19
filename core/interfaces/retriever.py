"""检索器抽象 — 可替换为向量库 / Elasticsearch 等实现。"""

from __future__ import annotations

from abc import ABC, abstractmethod

from domain.schemas import RetrievedChunk


class AbstractRetriever(ABC):
    """知识库检索统一接口。"""

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 1) -> list[RetrievedChunk]:
        """
        根据用户问题检索最相关的文档片段。

        Args:
            query: 用户自然语言问题
            top_k: 返回条数上限

        Returns:
            按相关性降序排列的 RetrievedChunk 列表
        """
        ...

    @abstractmethod
    def health_check(self) -> bool:
        """检索后端是否可用（向量库连接、索引就绪等）。"""
        ...
