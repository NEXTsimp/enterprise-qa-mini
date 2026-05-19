"""应用配置：通过环境变量注入，支持 .env 文件。"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# 固定从项目根目录加载 .env，避免 Streamlit 工作目录变化导致读不到配置
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

RetrieverBackend = Literal["bm25"]
LLMProvider = Literal["openai", "deepseek", "dashscope", "local", "mock"]

_PROVIDER_DEFAULTS: dict[str, dict[str, str | None]] = {
    "openai": {"base_url": None, "model": "gpt-4o-mini"},
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
    },
    "dashscope": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
    },
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    app_name: str = "Enterprise QA Mini"
    debug: bool = False

    # --- Retriever ---
    retriever_backend: RetrieverBackend = "bm25"
    retrieval_top_k_default: int = 1

    # --- LLM ---
    llm_provider: LLMProvider = "mock"
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str = ""
    llm_base_url: str | None = None
    llm_temperature: float = 0.1
    llm_max_tokens: int = 2048

    # --- Paths ---
    mock_docs_module: str = Field(
        default="data.mock_docs",
        description="Mock 文档数据源模块路径",
    )


def apply_provider_defaults(settings: Settings) -> Settings:
    """按厂商补全 base_url / 默认 model。"""
    defaults = _PROVIDER_DEFAULTS.get(settings.llm_provider, {})
    updates: dict[str, str | None] = {}
    if not settings.llm_base_url and defaults.get("base_url"):
        updates["llm_base_url"] = defaults["base_url"]
    if settings.llm_model == "gpt-4o-mini" and defaults.get("model"):
        if settings.llm_provider != "openai":
            updates["llm_model"] = defaults["model"]
    if updates:
        return settings.model_copy(update=updates)
    return settings


def get_settings() -> Settings:
    """每次读取最新 .env；override=True 避免系统里残留的 LLM_PROVIDER=openai 覆盖文件。"""
    if ENV_FILE.is_file():
        from dotenv import load_dotenv

        load_dotenv(ENV_FILE, override=True)
    return apply_provider_defaults(Settings())


def settings_debug_line(settings: Settings) -> str:
    base = settings.llm_base_url or "(OpenAI 官方 api.openai.com)"
    return f"provider={settings.llm_provider} | model={settings.llm_model} | endpoint={base}"
