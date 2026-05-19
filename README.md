# Enterprise QA Mini

企业制度 **RAG 智能问答**（Python + Streamlit）。分层架构、可演示、可扩展，适合作为 LLM 应用方向的作品集项目。

## 功能特性

- **RAG 问答**：BM25 + jieba 检索，单次大模型调用生成回答（流式输出）
- **多轮对话**：会话历史传入 LLM；寒暄、承接语（如「需要」「谢谢」）智能跳过检索
- **引用溯源**：展示检索片段与原文摘录（不额外调用摘要模型）
- **多会话**：侧栏历史对话、新建会话
- **多模型**：Mock（免 Key）、DashScope、DeepSeek、OpenAI 兼容、本地 Ollama

## 架构概览

```
app.py                 # Streamlit 薄 UI
├── ui/                # 组件、侧栏、会话存储
├── controllers/       # QAController（UI 唯一业务入口）
├── orchestration/     # QAPipeline：检索 → 问答
├── core/
│   ├── interfaces/    # AbstractRetriever / AbstractLLMService
│   ├── retrievers/    # BM25Retriever
│   ├── llm/           # OpenAI 兼容 / Mock / Local(Ollama)
│   ├── retrieval/     # 相关性过滤、多轮路由
│   └── services/      # QAService、引用摘录
├── domain/            # Pydantic 数据契约
├── config/            # Settings + Prompt
└── data/              # Mock 制度文档
```

| 原则 | 实现 |
|------|------|
| UI 与业务解耦 | `app.py` 只调用 `controllers`、`ui` |
| 接口驱动 | 抽象接口 + Factory 切换实现 |
| 类型安全 | `QueryRequest` / `QueryResult` / `PreparedQuery` 等 |
| 配置外置 | `.env` + `config/settings.py` |

## 快速开始

需要 **Python 3.10+**。

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          
streamlit run app.py
```


## 检索说明

默认 **BM25 + jieba**，面向内置 4 份短文档，毫秒级、零向量库依赖。扩展向量检索时：实现 `AbstractRetriever` 子类并在 `core/retrievers/factory.py` 注册即可。

## License

MIT
