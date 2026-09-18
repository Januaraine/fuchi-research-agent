"""Wikipedia 数据源适配器（Phase 4 首个真实数据源）。

仅使用标准库（urllib）+ 规范 User-Agent，无需额外依赖。
- `fetch_summary`          使用 REST API 获取页面摘要（标题 / 摘要 / 规范链接）
- `fetch_categories_links` 使用 Action API 获取分类与内部链接（用于分类映射与实体链接）
- `slugify`                将标题规整为与 seed 一致的 slug（用于去重 / 实体对齐）
"""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request

USER_AGENT = "KnowledgeObservatory/0.2 (educational project; local development)"

REST_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
ACTION_API = "https://en.wikipedia.org/w/api.php"


def _get_json(url: str, timeout: float = 25) -> dict:
    req = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def clean_extract(text: str, max_len: int = 900) -> str:
    """清洗摘要：合并空白、截断到合理长度（按词边界）。"""
    t = re.sub(r"\s+", " ", text).strip()
    if len(t) <= max_len:
        return t
    cut = t[:max_len]
    idx = cut.rfind(" ")
    return cut[:idx] if idx > 80 else cut


def slugify(title: str) -> str:
    """标题 → slug，与 seed_data 的 id 约定一致。

    "Transformer (deep learning)" -> "transformer"
    "Machine learning" -> "machine-learning"
    """
    s = title.lower().strip()
    s = re.sub(r"\s*\([^)]*\)\s*", " ", s)  # 去掉消歧义括号
    s = s.replace("_", " ")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def fetch_summary(title: str) -> dict:
    """获取页面摘要。返回 {title, extract, description, url}。"""
    safe = urllib.parse.quote(title, safe="")
    data = _get_json(REST_SUMMARY.format(title=safe))
    page_url = (
        data.get("content_urls", {})
        .get("desktop", {})
        .get("page")
        or f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
    )
    return {
        "title": data.get("title", title),
        "extract": clean_extract(data.get("extract", "")),
        "description": data.get("description", "") or "",
        "url": page_url,
    }


def fetch_categories_links(
    title: str, cllimit: int = 40, pllimit: int = 60
) -> tuple[list[str], list[str]]:
    """获取页面的分类与内部链接（普通词条命名空间）。"""
    params = urllib.parse.urlencode(
        {
            "action": "query",
            "titles": title,
            "prop": "categories|links",
            "cllimit": str(cllimit),
            "pllimit": str(pllimit),
            "plnamespace": "0",
            "format": "json",
            "redirects": "1",
        }
    )
    data = _get_json(f"{ACTION_API}?{params}")
    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return [], []
    page = next(iter(pages.values()))
    cats = [
        c["title"][len("Category:") :] if c["title"].startswith("Category:") else c["title"]
        for c in page.get("categories", [])
    ]
    links = [l["title"] for l in page.get("links", [])]
    return cats, links
