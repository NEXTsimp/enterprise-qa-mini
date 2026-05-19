"""无检索命中时的友好回复（寒暄 / 完全无关）。"""

from __future__ import annotations

from core.retrieval.relevance import is_social_chitchat
from data.mock_docs import MOCK_DOCS

_EXAMPLE_QUESTIONS = (
    "\u4f8b\u5982\uff1a\u5e74\u5047\u53ef\u4ee5\u7ed3\u8f6c\u51e0\u5929\uff1f"
    "\u62a5\u9500\u8d85\u8fc7 5000 \u5143\u8c01\u5ba1\u6279\uff1f"
    "\u65b0\u5458\u5de5 IT \u8d26\u53f7\u4f55\u65f6\u5f00\u901a\uff1f"
)


def _topic_list() -> str:
    return "\n".join(f"- {doc['title']}" for doc in MOCK_DOCS)


def build_fallback_reply(question: str) -> str:
    topics = _topic_list()
    if is_social_chitchat(question):
        return (
            "\u60a8\u597d\uff01\u6211\u662f\u4f01\u4e1a\u77e5\u8bc6\u5e93\u52a9\u624b\uff0c"
            "\u4e13\u6ce8\u516c\u53f8\u5185\u90e8\u5236\u5ea6\u4e0e\u6d41\u7a0b\u3002\n\n"
            "\u60a8\u53ef\u4ee5\u5411\u6211\u54a8\u8be2\uff1a\n"
            f"{topics}\n\n"
            f"{_EXAMPLE_QUESTIONS}"
        )

    q = question.strip()
    return (
        f"\u62b1\u6b49\uff0c\u5f53\u524d\u77e5\u8bc6\u5e93\u4e2d\u6ca1\u6709\u4e0e\u300c{q}\u300d"
        "\u76f8\u5173\u7684\u5236\u5ea6\u8bf4\u660e\uff0c\u6211\u65e0\u6cd5\u7ed9\u51fa\u51c6\u786e\u7b54\u6848\u3002\n\n"
        "\u8fd9\u91cc\u4e3b\u8981\u53ef\u4ee5\u5e2e\u60a8\u89e3\u7b54\uff1a\n"
        f"{topics}\n\n"
        f"{_EXAMPLE_QUESTIONS}\n\n"
        "\u8bf7\u6362\u4e00\u4e2a\u4e0e\u4e0a\u8ff0\u4e3b\u9898\u76f8\u5173\u7684\u95ee\u9898\u8bd5\u8bd5\u3002"
    )
