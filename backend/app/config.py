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
