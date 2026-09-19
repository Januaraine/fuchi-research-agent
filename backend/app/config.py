import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_dotenv(path: Path) -> None:
    """极简 .env 加载（无第三方依赖）。

    读取 backend/.env 中的 `KEY=VALUE` 行写入 os.environ（已存在的环境变量优先，不会被覆盖）。
    真实密钥只放在本地 .env，绝不提交到仓库。
    """
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if key:
            os.environ.setdefault(key, value)


# 本地密钥从 backend/.env 读取（若存在）；未设置则回落到真实环境变量。
_load_dotenv(BASE_DIR / ".env")

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
