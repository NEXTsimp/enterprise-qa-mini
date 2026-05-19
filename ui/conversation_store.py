# -*- coding: utf-8 -*-
"""Streamlit session: multi-chat storage, switch, and LLM history."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

import streamlit as st

from core.interfaces.llm import LLMMessage

MAX_CONVERSATIONS = 30
_DEFAULT_TITLE = "\u65b0\u5bf9\u8bdd"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _title_from_messages(messages: list[dict[str, Any]]) -> str:
    for msg in messages:
        if msg.get("role") == "user":
            text = (msg.get("content") or "").strip()
            if text:
                return text[:28] + ("\u2026" if len(text) > 28 else "")
    return _DEFAULT_TITLE


def _new_conversation_record(cid: str | None = None) -> dict[str, Any]:
    conv_id = cid or str(uuid.uuid4())
    return {
        "id": conv_id,
        "title": _DEFAULT_TITLE,
        "messages": [],
        "updated_at": _now_iso(),
    }


def init_conversation_state() -> None:
    if "conversations" not in st.session_state:
        cid = str(uuid.uuid4())
        st.session_state.conversations = {cid: _new_conversation_record(cid)}
        st.session_state.current_conversation_id = cid
        st.session_state.messages = []
    elif "messages" not in st.session_state:
        cid = st.session_state.current_conversation_id
        st.session_state.messages = list(
            st.session_state.conversations[cid]["messages"]
        )


def _prune_empty_conversations() -> None:
    current = st.session_state.current_conversation_id
    for cid in list(st.session_state.conversations):
        if cid != current and not st.session_state.conversations[cid].get("messages"):
            del st.session_state.conversations[cid]


def sync_current_conversation() -> None:
    init_conversation_state()
    cid = st.session_state.current_conversation_id
    conv = st.session_state.conversations.setdefault(cid, _new_conversation_record(cid))
    conv["messages"] = list(st.session_state.get("messages", []))
    conv["updated_at"] = _now_iso()
    conv["title"] = _title_from_messages(conv["messages"])
    _prune_empty_conversations()
    _trim_conversations()


def _trim_conversations() -> None:
    convs = st.session_state.conversations
    if len(convs) <= MAX_CONVERSATIONS:
        return
    current = st.session_state.current_conversation_id
    ordered = sorted(convs.values(), key=lambda c: c["updated_at"], reverse=True)
    for conv in ordered[MAX_CONVERSATIONS:]:
        if conv["id"] != current:
            convs.pop(conv["id"], None)


def start_new_conversation() -> None:
    init_conversation_state()
    sync_current_conversation()
    if not st.session_state.messages:
        st.session_state.pop("auto_ask", None)
        return
    new_id = str(uuid.uuid4())
    st.session_state.conversations[new_id] = _new_conversation_record(new_id)
    st.session_state.current_conversation_id = new_id
    st.session_state.messages = []
    st.session_state.pop("auto_ask", None)


def switch_conversation(conversation_id: str) -> None:
    init_conversation_state()
    if (
        conversation_id == st.session_state.current_conversation_id
        or conversation_id not in st.session_state.conversations
    ):
        return
    sync_current_conversation()
    st.session_state.current_conversation_id = conversation_id
    st.session_state.messages = list(
        st.session_state.conversations[conversation_id]["messages"]
    )
    st.session_state.pop("auto_ask", None)


def list_conversations_newest_first() -> list[dict[str, Any]]:
    init_conversation_state()
    return sorted(
        st.session_state.conversations.values(),
        key=lambda c: c["updated_at"],
        reverse=True,
    )


def _assistant_text(msg: dict[str, Any]) -> str:
    content = (msg.get("content") or "").strip()
    if content:
        return content
    result = msg.get("result")
    if result is None:
        return ""
    if hasattr(result, "answer"):
        return (result.answer or "").strip()
    if isinstance(result, dict):
        return (result.get("answer") or "").strip()
    return ""


def session_messages_to_history(
    messages: list[dict[str, Any]],
    *,
    exclude_last: bool = True,
) -> list[LLMMessage]:
    items = messages[:-1] if exclude_last and messages else list(messages)
    out: list[LLMMessage] = []
    for msg in items:
        role = msg.get("role")
        if role == "user":
            text = (msg.get("content") or "").strip()
        elif role == "assistant":
            text = _assistant_text(msg)
        else:
            continue
        if text:
            out.append(LLMMessage(role=role, content=text))
    return out
