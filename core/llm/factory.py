"""LLM 工厂 — 根据 LLM_PROVIDER 切换实现。"""

from __future__ import annotations

from config.settings import Settings, apply_provider_defaults, get_settings
from core.interfaces.llm import AbstractLLMService
from core.llm.mock_llm import MockLLMService
from core.llm.openai_compatible import OpenAICompatibleLLM


def create_llm_service(settings: Settings | None = None) -> AbstractLLMService:
    cfg = apply_provider_defaults(settings or get_settings())

    if cfg.llm_provider == "mock":
        return MockLLMService()

    if cfg.llm_provider == "local":
        from core.llm.local_llm import LocalLLMService

        endpoint = cfg.llm_base_url or "http://localhost:11434"
        if endpoint.endswith("/v1"):
            endpoint = endpoint[: -len("/v1")]
        return LocalLLMService(endpoint=endpoint, model=cfg.llm_model)

    return OpenAICompatibleLLM(cfg)
