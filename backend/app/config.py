import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# 默认使用项目内的 SQLite 文件；可通过 DATABASE_URL 覆盖（例如后续切 PostgreSQL）。
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'knowledge.db'}")

# CORS 允许的前端来源（本地开发默认 Next.js）。
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")

# LLM（OpenAI 兼容接口，Phase 6）。未配置 base/key 时 RAG 仅检索不生成。
# 示例：DeepSeek  LLM_API_BASE=https://api.deepseek.com   LLM_MODEL=deepseek-chat
#       OpenAI   LLM_API_BASE=https://api.openai.com/v1   LLM_MODEL=gpt-4o-mini
#       Ollama   LLM_API_BASE=http://localhost:11434/v1   LLM_MODEL=llama3
LLM_API_BASE = os.getenv("LLM_API_BASE", "").strip() or None
LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip() or None
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")
