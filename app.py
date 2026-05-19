"""Streamlit entrypoint — chat layout with bottom input."""

from __future__ import annotations

import html

import streamlit as st
from openai import APIStatusError, RateLimitError

from config.settings import get_settings
from controllers.qa_controller import QAController
from domain.schemas import QueryResult
from ui.conversation_store import (
    init_conversation_state,
    session_messages_to_history,
    sync_current_conversation,
)
from ui.components import (
    inject_styles,
    render_assistant_citations,
    render_chat_history,
    render_sidebar,
    render_welcome,
)

settings = get_settings()


def _ready() -> bool:
    if settings.llm_provider == "mock":
        return True
    k = settings.llm_api_key.strip()
    return bool(k) and "your-key" not in k.lower()


def _stream_assistant_reply(question: str) -> None:
    q = question.strip()
    history = session_messages_to_history(
        st.session_state.messages, exclude_last=True
    )
    controller = QAController()

    try:
        with st.spinner("检索相关资料…"):
            prepared = controller.prepare(q, history=history)

        with st.chat_message("assistant"):
            if prepared.fallback_answer is not None:
                answer = prepared.fallback_answer
                st.markdown(answer)
            else:
                answer = st.write_stream(controller.stream_answer(prepared))

            result = QueryResult(
                question=q,
                answer=answer,
                citations=prepared.citations,
                summaries=prepared.summaries,
            )
            if result.citations or result.summaries:
                with st.expander("查看引用", expanded=False):
                    render_assistant_citations(result)

        st.session_state.messages.append(
            {"role": "assistant", "result": result, "content": answer}
        )
    except (RateLimitError, APIStatusError) as e:
        with st.chat_message("assistant"):
            st.markdown(f"模型调用失败：{e}")
        st.session_state.messages.append(
            {"role": "assistant", "content": f"模型调用失败：{e}"}
        )
    except Exception as e:
        with st.chat_message("assistant"):
            st.markdown(f"处理失败：{e}")
        st.session_state.messages.append(
            {"role": "assistant", "content": f"处理失败：{e}"}
        )
    sync_current_conversation()


def _handle_question(question: str) -> None:
    q = question.strip()
    if not q:
        return
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(html.escape(q))
    if not _ready():
        with st.chat_message("assistant"):
            st.markdown("请在 .env 配置 LLM_API_KEY，或设置 LLM_PROVIDER=mock")
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": "请在 .env 配置 LLM_API_KEY，或设置 LLM_PROVIDER=mock",
            }
        )
        sync_current_conversation()
        return
    _stream_assistant_reply(q)


st.set_page_config(
    page_title=settings.app_name,
    page_icon="\U0001f3e2",
    layout="centered",
    initial_sidebar_state="expanded",
)

init_conversation_state()

inject_styles()
render_sidebar(settings)
sync_current_conversation()

# 待处理问题（来自快捷芯片或上一轮 chat_input 写入）
pending_question: str | None = None
if ask := st.session_state.pop("auto_ask", None):
    pending_question = ask.strip() or None
if queued := st.session_state.pop("_eqa_pending_input", None):
    pending_question = (queued or "").strip() or pending_question

render_chat_history()

# 仅在没有历史消息且本轮不会立刻提问时展示欢迎页
if not st.session_state.messages and pending_question is None:
    render_welcome()

# 底部输入：先写入 session 再 rerun，避免与欢迎页同屏
if prompt := st.chat_input(
    "\u53d1\u6d88\u606f\u2026",
    key="eqa_chat_input",
):
    text = prompt.strip()
    if text:
        st.session_state._eqa_pending_input = text
        st.rerun()

if pending_question:
    _handle_question(pending_question)
