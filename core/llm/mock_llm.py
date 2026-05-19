"""离线 Mock LLM — 无 API Key / 无额度时演示检索与 UI 流程。"""

from __future__ import annotations

import re
from collections.abc import Iterator

from core.interfaces.llm import AbstractLLMService, LLMMessage


class MockLLMService(AbstractLLMService):
    def chat(self, messages: list[LLMMessage], **kwargs) -> str:
        system_text = next((m.content for m in messages if m.role == "system"), "")
        user_text = next((m.content for m in reversed(messages) if m.role == "user"), "")

        if "多轮对话" in system_text and "【参考资料】" not in user_text:
            return self._mock_conversation(messages, user_text)
        return self._mock_qa(user_text)

    def chat_stream(self, messages: list[LLMMessage], **kwargs) -> Iterator[str]:
        text = self.chat(messages, **kwargs)
        step = 12
        for i in range(0, len(text), step):
            yield text[i : i + step]

    def health_check(self) -> bool:
        return True

    @staticmethod
    def _extract_block(text: str, label: str) -> str:
        pattern = rf"【{re.escape(label)}】\s*\n?(.*?)(?=\n【|\Z)"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _mock_conversation(messages: list[LLMMessage], question: str) -> str:
        last_assistant = ""
        for m in messages:
            if m.role == "assistant":
                last_assistant = m.content
        q = question.strip()
        hint = "（Mock 模式，配置真实 LLM 后会继续上文回答）"
        compact = re.sub(r"[\s,，。.!！?？]+", "", question)
        if any(k in compact for k in ("谢", "感谢", "thanks", "thx", "辛苦")):
            if last_assistant and any(
                k in last_assistant for k in ("年假", "报销", "制度")
            ):
                return (
                    f"不客气～能帮上忙就好。"
                    f"之后还有制度方面的问题，随时找我。{hint}"
                )
            return f"不客气～随时找我。{hint}"
        if q in ("需要", "好的", "好", "行", "可以", "没问题", "是的"):
            if last_assistant:
                return (
                    f"好的，我继续说明："
                    f"关于您刚才问的内容，"
                    f"我可以按步骤展开。{hint}"
                )
            return f"好的，请告诉我您具体想了解哪一块。{hint}"
        if q in ("不用了", "不用", "不要", "算了", "取消"):
            return f"好的，那先不打扰了。之后有制度问题随时找我。{hint}"
        return (
            f"你好！我是企业知识库小助手，"
            f"请假、报销、IT 开通等问题都可以问我。{hint}"
        )

    def _mock_qa(self, user_text: str) -> str:
        title_match = re.search(r"标题：(.+)", user_text)
        title = title_match.group(1).strip() if title_match else "参考资料"
        content = self._extract_block(user_text, "参考资料") or user_text
        question = self._extract_block(user_text, "用户问题") or "您的问题"

        snippet = content[:280] + ("…" if len(content) > 280 else "")
        return (
            f"（Mock 模式，未调用真实大模型）\n\n"
            f"根据《{title}》，针对「{question.strip()}」：\n\n"
            f"{snippet}\n\n"
            f"如需更自然的表述，请在 `.env` 中将 `LLM_PROVIDER` 改为 `dashscope` 或 `deepseek` 并配置 API Key。"
        )
