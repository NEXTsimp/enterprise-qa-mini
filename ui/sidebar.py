# -*- coding: utf-8 -*-
"""Sidebar UI — modern AI SaaS style (Streamlit + CSS)."""

from __future__ import annotations

import html

import streamlit as st

from config.settings import Settings, settings_debug_line
from ui.conversation_store import (
    list_conversations_newest_first,
    start_new_conversation,
    switch_conversation,
)

_D = "div"

_LOGO_SVG = (
    '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" '
    'xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<rect x="2" y="3" width="20" height="18" rx="5" fill="#111827"/>'
    '<path d="M8 10h8M8 14h5" stroke="#fff" stroke-width="1.6" '
    'stroke-linecap="round"/></svg>'
)

SIDEBAR_CSS = """
<style>
    [data-testid="stSidebar"] {
        width: 260px !important;
        min-width: 260px !important;
        max-width: 260px !important;
        background: #f7f7f8 !important;
        border-right: 1px solid #e5e7eb !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        width: 260px !important;
        background: #f7f7f8 !important;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        background: #f7f7f8 !important;
    }
    [data-testid="stSidebarUserContent"] {
        display: flex !important;
        flex-direction: column !important;
        min-height: 100dvh !important;
        padding: 18px 14px 14px !important;
        background: linear-gradient(180deg, #f7f7f8 0%, #f3f4f6 100%) !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    [data-testid="stSidebarUserContent"] [data-testid="stElementContainer"] {
        margin-bottom: 0 !important;
    }

    .eqa-brand-row {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0 2px 18px;
        margin-bottom: 8px;
        border-bottom: 1px solid #e5e7eb;
        flex-shrink: 0;
    }
    .eqa-logo-icon {
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .eqa-brand-text { min-width: 0; }
    .eqa-brand-title {
        font-size: 15px;
        font-weight: 600;
        color: #18181b;
        line-height: 1.35;
        margin: 0;
        letter-spacing: -0.01em;
    }
    .eqa-brand-sub {
        font-size: 12px;
        color: #a1a1aa;
        margin: 3px 0 0;
        line-height: 1.4;
    }
    .eqa-hist-label {
        font-size: 12px;
        font-weight: 500;
        color: #a1a1aa;
        letter-spacing: 0;
        margin: 16px 0 10px 6px;
    }
    .eqa-hist-empty { padding: 10px 6px 14px; }
    .eqa-hist-empty-title {
        font-size: 13px;
        color: #9ca3af;
        margin: 0 0 4px;
    }
    .eqa-hist-empty-hint {
        font-size: 12px;
        color: #c4c4c4;
        margin: 0;
    }

    [data-testid="stSidebar"] .st-key-btn_new_chat {
        margin-bottom: 14px !important;
        flex-shrink: 0;
    }
    [data-testid="stSidebar"] .st-key-btn_new_chat button {
        width: 100% !important;
        background: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 12px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 10px 14px !important;
        min-height: 2.65rem !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.2s ease !important;
        justify-content: flex-start !important;
    }
    [data-testid="stSidebar"] .st-key-btn_new_chat button:hover {
        background: #f3f4f6 !important;
        border-color: #d1d5db !important;
        transform: translateY(-1px);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06) !important;
    }

    [data-testid="stSidebarUserContent"] [class*="st-key-conv_"] {
        margin-bottom: 2px !important;
    }
    [data-testid="stSidebarUserContent"] [class*="st-key-conv_"] button {
        width: 100% !important;
        border: none !important;
        border-radius: 10px !important;
        font-size: 13px !important;
        line-height: 1.45 !important;
        padding: 10px 12px !important;
        min-height: 2.5rem !important;
        text-align: left !important;
        justify-content: flex-start !important;
        background: transparent !important;
        color: #374151 !important;
        box-shadow: none !important;
        transition: background 0.15s ease !important;
    }
    [data-testid="stSidebarUserContent"] [class*="st-key-conv_"] button p {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap !important;
    }
    [data-testid="stSidebarUserContent"] [class*="st-key-conv_"] button:hover {
        background: #ececf1 !important;
        color: #111827 !important;
    }
    [data-testid="stSidebarUserContent"] [class*="st-key-conv_"] button[kind="primary"] {
        background: #ececf1 !important;
        color: #111827 !important;
        font-weight: 500 !important;
    }

    [data-testid="stSidebarUserContent"] [data-testid="stExpander"] {
        margin-top: auto !important;
        flex-shrink: 0;
        padding-top: 12px !important;
        border-top: 1px solid #e5e7eb;
        background: transparent !important;
        border-left: none !important;
        border-right: none !important;
        border-bottom: none !important;
    }
    [data-testid="stSidebarUserContent"] [data-testid="stExpander"] summary {
        display: flex !important;
        align-items: center !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        color: #374151 !important;
        padding: 10px 10px !important;
        border-radius: 10px !important;
        transition: background 0.15s ease !important;
        list-style: none !important;
    }
    [data-testid="stSidebarUserContent"] [data-testid="stExpander"] summary:hover {
        background: #ececf1 !important;
    }
    [data-testid="stSidebarUserContent"] [data-testid="stExpander"] [data-testid="stCaptionContainer"] {
        font-size: 12px !important;
        color: #6b7280 !important;
    }

    @media (prefers-color-scheme: dark) {
        [data-testid="stSidebar"],
        [data-testid="stSidebarUserContent"] {
            background: #18181b !important;
            border-color: #27272a !important;
        }
        .eqa-brand-row { border-color: #27272a; }
        .eqa-brand-title { color: #fafafa; }
        .eqa-brand-sub, .eqa-hist-label, .eqa-hist-empty-title { color: #71717a; }
        [data-testid="stSidebar"] .st-key-btn_new_chat button {
            background: #27272a !important;
            border-color: #3f3f46 !important;
            color: #fafafa !important;
        }
        [data-testid="stSidebarUserContent"] [class*="st-key-conv_"] button { color: #d4d4d8; }
        [data-testid="stSidebarUserContent"] [class*="st-key-conv_"] button:hover,
        [data-testid="stSidebarUserContent"] [class*="st-key-conv_"] button[kind="primary"] {
            background: #3f3f46 !important;
            color: #fafafa !important;
        }
        [data-testid="stSidebarUserContent"] [data-testid="stExpander"] {
            border-color: #27272a !important;
        }
    }
</style>
"""


def inject_sidebar_styles() -> None:
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)


def _render_brand(app_name: str) -> None:
    safe = html.escape(app_name)
    st.markdown(
        f'<{_D} class="eqa-brand-row">'
        f'<{_D} class="eqa-logo-icon">{_LOGO_SVG}</{_D}>'
        f'<{_D} class="eqa-brand-text">'
        f'<p class="eqa-brand-title">{safe}</p>'
        f'<p class="eqa-brand-sub">\u4f01\u4e1a\u5236\u5ea6\u667a\u80fd\u95ee\u7b54</p>'
        f"</{_D}></{_D}>",
        unsafe_allow_html=True,
    )


def render_sidebar(settings: Settings) -> None:
    labels = {
        "mock": "Mock",
        "dashscope": "DashScope",
        "deepseek": "DeepSeek",
        "openai": "OpenAI",
    }
    provider = labels.get(settings.llm_provider, settings.llm_provider)
    expander_label = f"\u2699  {provider} \u00b7 {settings.llm_model}"

    with st.sidebar:
        _render_brand(settings.app_name)

        if st.button(
            "\uFF0B  \u65b0\u5bf9\u8bdd",
            use_container_width=True,
            key="btn_new_chat",
            type="secondary",
        ):
            start_new_conversation()
            st.rerun()

        st.markdown('<p class="eqa-hist-label">\u5386\u53f2\u5bf9\u8bdd</p>', unsafe_allow_html=True)

        current_id = st.session_state.get("current_conversation_id")
        shown = [c for c in list_conversations_newest_first() if c.get("messages")]

        if not shown:
            st.markdown(
                f'<{_D} class="eqa-hist-empty">'
                f'<p class="eqa-hist-empty-title">\u6682\u65e0\u5386\u53f2\u8bb0\u5f55</p>'
                f'<p class="eqa-hist-empty-hint">\u5f00\u59cb\u4f60\u7684\u7b2c\u4e00\u6b21\u63d0\u95ee</p>'
                f"</{_D}>",
                unsafe_allow_html=True,
            )

        for conv in shown:
            cid = conv["id"]
            title = conv.get("title") or "\u65b0\u5bf9\u8bdd"
            is_current = cid == current_id
            if st.button(
                title,
                key=f"conv_{cid}",
                use_container_width=True,
                type="primary" if is_current else "secondary",
            ):
                if not is_current:
                    switch_conversation(cid)
                    st.rerun()

        with st.expander(expander_label, expanded=False):
            st.caption(f"LLM\uFF1a{provider}")
            st.caption(f"\u6a21\u578b\uFF1a{settings.llm_model}")
            st.caption("\u68c0\u7d22\uFF1aBM25")
            st.caption(settings_debug_line(settings))
