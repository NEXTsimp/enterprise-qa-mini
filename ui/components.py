# -*- coding: utf-8 -*-
"""Streamlit UI ? Doubao-inspired layout and typography."""

from __future__ import annotations

import html

import streamlit as st

from config.settings import Settings
from domain.schemas import QueryResult, SummaryOutput
from ui.sidebar import inject_sidebar_styles, render_sidebar

_STYLES = """
<style>
    html, body, [data-testid="stAppViewContainer"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
            "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
        font-size: 15px;
        color: #18181b;
    }
    [data-testid="stAppViewContainer"] > .main {
        background: #ffffff;
    }
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 6rem;
        max-width: 44rem;
        margin: 0 auto;
    }
    [data-testid="stHeader"] { background: transparent; }

    /* Bottom chat input ? Doubao-like pill */
    [data-testid="stBottomBlockContainer"] {
        padding: 0 1rem 1.25rem;
    }
    [data-testid="stChatInput"] {
        max-width: 44rem;
        margin: 0 auto;
    }
    [data-testid="stChatInput"] textarea {
        font-size: 15px !important;
        line-height: 1.5 !important;
        border-radius: 16px !important;
        padding: 12px 16px !important;
        border: 1px solid #e4e4e7 !important;
        background: #fafafa !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: #d4d4d8 !important;
        box-shadow: 0 0 0 3px rgba(24, 24, 27, 0.06) !important;
    }

    /* Chat bubbles */
    div[data-testid="stChatMessage"] {
        margin-bottom: 1.25rem !important;
        padding: 0.2rem 0 !important;
        align-items: flex-start !important;
    }
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        max-width: 88%;
        line-height: 1.7;
        font-size: 15px;
        letter-spacing: 0.01em;
    }
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        flex-direction: row-reverse !important;
    }
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
    [data-testid="stMarkdownContainer"] {
        margin-left: auto !important;
        margin-right: 0 !important;
        background: #f4f4f5;
        color: #18181b;
        border-radius: 16px 16px 4px 16px;
        padding: 0.7rem 1rem;
        border: none;
        box-shadow: none;
    }
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
    [data-testid="stMarkdownContainer"] {
        margin-right: auto !important;
        margin-left: 0 !important;
        background: transparent;
        color: #18181b;
        border: none;
        border-radius: 0;
        padding: 0.25rem 0;
        box-shadow: none;
    }
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
    [data-testid="stExpander"] {
        max-width: 100%;
        margin-top: 0.5rem;
        font-size: 13px;
    }

    /* Welcome ? centered hero */
    .eqa-welcome-wrap {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 36vh;
        text-align: center;
        padding: 1.5rem 1rem 1rem;
    }
    [data-testid="stMarkdownContainer"] .eqa-welcome-title,
    .eqa-welcome-wrap .eqa-welcome-title {
        font-size: 44px !important;
        font-weight: 600 !important;
        color: #18181b !important;
        line-height: 1.25 !important;
        margin: 0 0 16px 0 !important;
        letter-spacing: -0.03em !important;
    }
    @media (min-width: 640px) {
        [data-testid="stMarkdownContainer"] .eqa-welcome-title,
        .eqa-welcome-wrap .eqa-welcome-title {
            font-size: 44px !important;
        }
    }
    .eqa-welcome-sub {
        color: #a1a1aa;
        font-size: 14px;
        font-weight: 400;
        margin: 0 0 28px 0;
        max-width: 22rem;
        line-height: 1.55;
    }

    /* Suggestion chips ? 2x2, light gray cards */
    [class*="st-key-chip_"] {
        padding: 0 5px !important;
    }
    [class*="st-key-chip_"] button {
        width: 100% !important;
        border-radius: 12px !important;
        border: none !important;
        background: #f4f4f5 !important;
        color: #3f3f46 !important;
        font-size: 13px !important;
        font-weight: 400 !important;
        line-height: 1.45 !important;
        padding: 11px 14px !important;
        min-height: 2.75rem !important;
        white-space: normal !important;
        text-align: left !important;
        justify-content: flex-start !important;
        box-shadow: none !important;
        transition: background 0.15s ease !important;
    }
    [class*="st-key-chip_"] button:hover {
        background: #ececef !important;
        color: #18181b !important;
    }
    [class*="st-key-chip_"] button p {
        font-size: 13px !important;
        line-height: 1.45 !important;
    }
</style>
"""

_WELCOME_TITLE = "\u6709\u4ec0\u4e48\u6211\u80fd\u5e2e\u4f60\u7684\u5417\uff1f"
_WELCOME_SUB = "\u57fa\u4e8e\u4f01\u4e1a\u5185\u90e8\u5236\u5ea6\u7684\u667a\u80fd\u95ee\u7b54\uff0c\u652f\u6301\u591a\u8f6e\u4e0e\u5f15\u7528\u6eaf\u6e90"
_SUGGESTIONS = [
    "\u5e74\u5047\u53ef\u4ee5\u7ed3\u8f6c\u51e0\u5929\uff1f",
    "\u62a5\u9500\u8d85\u8fc7 5000 \u5143\u8c01\u5ba1\u6279\uff1f",
    "\u65b0\u5458\u5de5 IT \u8d26\u53f7\u4f55\u65f6\u5f00\u901a\uff1f",
    "\u8fdc\u7a0b\u529e\u516c\u5b89\u5168\u8981\u6c42\u6709\u54ea\u4e9b\uff1f",
]
_LBL_EXCERPT = "\u5f15\u7528\u6458\u5f55"
_LBL_SOURCE = "\u6765\u6e90\uff1a"
_LBL_EXPANDER = "\u67e5\u770b\u5f15\u7528"


def inject_styles() -> None:
    st.markdown(_STYLES, unsafe_allow_html=True)
    inject_sidebar_styles()


def render_welcome() -> None:
    st.markdown(
        f'<div class="eqa-welcome-wrap">'
        f'<p class="eqa-welcome-title">{_WELCOME_TITLE}</p>'
        f'<p class="eqa-welcome-sub">{_WELCOME_SUB}</p>'
        f"</div>",
        unsafe_allow_html=True,
    )
    row1 = st.columns(2, gap="small")
    row2 = st.columns(2, gap="small")
    for i, text in enumerate(_SUGGESTIONS):
        col = row1[i] if i < 2 else row2[i - 2]
        with col:
            if st.button(text, key=f"chip_{i}", use_container_width=True):
                st.session_state.auto_ask = text
                st.rerun()


def _summary_md(summary: SummaryOutput) -> str:
    return summary.raw_markdown.strip() or "\u2014"


def _render_citations_block(result: QueryResult) -> None:
    if result.citations:
        for i, c in enumerate(result.citations, 1):
            ch = c.chunk
            st.markdown(
                f"**[{i}] {html.escape(ch.title)}** "
                f"<span style='color:#a1a1aa;font-size:12px'>"
                f"({c.score:.2f})</span>",
                unsafe_allow_html=True,
            )
            st.caption(ch.doc_id)
            st.text(ch.content[:300] + ("..." if len(ch.content) > 300 else ""))
    if result.summaries:
        st.markdown(f"**{_LBL_EXCERPT}**")
        for i, (c, s) in enumerate(zip(result.citations, result.summaries), 1):
            if result.citations:
                st.caption(f"{_LBL_SOURCE}{html.escape(c.chunk.title)}")
            st.markdown(_summary_md(s))


def render_assistant_citations(result: QueryResult) -> None:
    if not result.citations and not result.summaries:
        return
    _render_citations_block(result)


def render_assistant_result(result: QueryResult) -> None:
    st.markdown(result.answer)
    if not result.citations and not result.summaries:
        return
    with st.expander(_LBL_EXPANDER, expanded=False):
        render_assistant_citations(result)


def render_chat_history() -> None:
    for msg in st.session_state.get("messages", []):
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(html.escape(msg["content"]))
            elif msg.get("result"):
                render_assistant_result(msg["result"])
            else:
                st.markdown(msg.get("content", ""))


__all__ = [
    "inject_styles",
    "render_sidebar",
    "render_welcome",
    "render_assistant_citations",
    "render_assistant_result",
    "render_chat_history",
]
