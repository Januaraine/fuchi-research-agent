"""LLM 客户端（Phase 6）—— OpenAI 兼容接口。

仅使用标准库（urllib），不引入额外依赖。通过环境变量配置：
    LLM_API_BASE  例如 https://api.deepseek.com / https://api.openai.com/v1
    LLM_API_KEY   服务方密钥（本地 Ollama 可留空）
    LLM_MODEL     例如 deepseek-chat / gpt-4o-mini / llama3

同一套代码即可切换 DeepSeek / OpenAI / 本地 Ollama / vLLM 等任何
OpenAI 兼容的服务，只需改环境变量。
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

from ..config import LLM_API_BASE, LLM_API_KEY, LLM_MODEL


class LLMError(Exception):
    """LLM 调用失败。"""


class LLMClient:
    def __init__(self, base: str | None = None, key: str | None = None, model: str | None = None):
        self.base = (base if base is not None else LLM_API_BASE)
        self.base = self.base.rstrip("/") if self.base else None
        self.key = key if key is not None else LLM_API_KEY
        self.model = model or LLM_MODEL

    @property
    def configured(self) -> bool:
        return bool(self.base and self.model)

    def chat(self, system: str, user: str, temperature: float = 0.2, max_tokens: int = 900) -> str:
        if not self.configured:
            raise LLMError("LLM not configured (LLM_API_BASE / LLM_MODEL missing)")

        url = f"{self.base}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {"Content-Type": "application/json"}
        if self.key:
            headers["Authorization"] = f"Bearer {self.key}"

        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")[:300]
            raise LLMError(f"HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise LLMError(f"network error: {exc.reason}") from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"unexpected response: {json.dumps(data)[:300]}") from exc
        return str(content).strip()
