"""检索结果相关性过滤 — 无关/闲聊/多轮承接不返回引用。"""

from __future__ import annotations

import re

import jieba

from core.interfaces.llm import LLMMessage
from domain.schemas import RetrievedChunk

_CHITCHAT = re.compile(
    r"^\s*("
    r"你好|您好|嗨|hi|hello|在吗|在不在|"
    r"谢谢|多谢|感谢|thanks|thx|不客气|辛苦了|"
    r"早上好|中午好|下午好|晚上好|晚安|"
    r"再见|拜拜|bye|"
    r"你是谁|你叫什么|你能做什么|你会什么|"
    r"好的|嗯|嗯嗯|ok|okay|收到"
    r")[\s!?！？。~～…]*$",
    re.IGNORECASE,
)

_FOLLOW_UP = re.compile(
    r"^\s*("
    r"需要|不需要|不用了|不用|不要|"
    r"好的|好呀|好啊|好哒|行|可以|没问题|"
    r"是的|不是|对|不对|嗯嗯|"
    r"继续|算了|取消|告辞|再见"
    r")[\s!?！？。~～…]*$",
    re.IGNORECASE,
)

_STOPWORDS = frozenset(
    {"你好", "您好", "请问", "什么", "怎么", "吗", "呢", "的", "了", "是", "有", "在"}
)


def _query_tokens(query: str) -> set[str]:
    text = re.sub(r"\s+", "", query)
    return {t for t in jieba.cut_for_search(text) if len(t.strip()) >= 2} - _STOPWORDS


def is_social_chitchat(query: str) -> bool:
    return bool(_CHITCHAT.match(query.strip()))


def is_follow_up_reply(query: str, history: list[LLMMessage]) -> bool:
    if not history or history[-1].role != "assistant":
        return False
    q = query.strip()
    return len(q) <= 16 and bool(_FOLLOW_UP.match(q))


def should_skip_retrieval(query: str, history: list[LLMMessage]) -> bool:
    return is_social_chitchat(query) or is_follow_up_reply(query, history)


def filter_relevant_citations(
    query: str,
    citations: list[RetrievedChunk],
    *,
    history: list[LLMMessage] | None = None,
    min_score_ratio: float = 0.35,
    min_absolute_score: float = 0.8,
) -> list[RetrievedChunk]:
    hist = history or []
    if not citations or should_skip_retrieval(query, hist):
        return []
    tokens = _query_tokens(query)
    if not tokens:
        return []

    max_score = max(c.score for c in citations)
    if max_score < min_absolute_score:
        return []

    score_floor = max(max_score * min_score_ratio, min_absolute_score)
    kept: list[RetrievedChunk] = []
    for c in citations:
        text = f"{c.chunk.title} {c.chunk.content}"
        if c.score >= score_floor and any(t in text for t in tokens):
            kept.append(c)
    return kept
