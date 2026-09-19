"""RAG 查询层（Phase 6）。

流程：
    User Question
        ↓
    向量检索（Phase 5 embedding_service）+ 关键词兜底
        ↓
    Retrieve Sources
        ↓
    [LLM 已配置] Grounded Answer（带 [n] 来源引用）
    [LLM 未配置] 仅返回检索结果（retrieval_ready_no_llm）
    [无相关资料] 明确说明，不强行生成
"""
from __future__ import annotations

import re

from sqlalchemy.orm import Session

from .. import models
from . import embedding_service
from .llm import LLMClient, LLMError

SYSTEM_PROMPT = (
    "You are the Knowledge Observatory's retrieval-augmented answering engine. "
    "Answer ONLY using the numbered knowledge-node context provided. "
    "If the context does not contain enough information, say explicitly that the "
    "information was not found and do not fabricate. "
    "Cite each claim inline with [1] [2] ... matching the numbered list. "
    "Answer concisely in the same language as the question."
)

STOPWORDS = {
    "the", "and", "for", "are", "was", "were", "what", "how", "why", "when",
    "where", "which", "who", "this", "that", "with", "from", "into", "about",
    "between", "does", "should", "would", "could", "can", "not", "your", "you",
    "its", "they", "them", "their", "there", "here", "has", "have", "had",
    "been", "being", "will", "shall", "may", "might", "must", "some", "such",
    "than", "then", "also", "but", "get", "got", "use", "used", "using",
    "like", "just", "via", "per", "etc", "relation", "related", "relationship",
    "explain", "describe", "difference", "compare", "tell",
}


class RAGService:
    def __init__(self, db: Session):
        self.db = db

    def _keyword_search(self, question: str, k: int) -> list[tuple[models.KnowledgeNode, float]]:
        """关键词检索（兜底）：按 token 在名称/描述/分类中加权匹配。"""
        tokens = [
            w for w in re.findall(r"[a-zA-Z0-9]+", question.lower())
            if len(w) > 2 and w not in STOPWORDS
        ]
        if not tokens:
            return []
        scored: list[tuple[models.KnowledgeNode, float]] = []
        for node in self.db.query(models.KnowledgeNode).all():
            name = node.name.lower()
            text = f"{name} {node.description.lower()} {node.category.lower()}"
            score = 0.0
            for token in tokens:
                if token in name:
                    score += 3.0
                elif token in text:
                    score += 1.0
            if score > 0:
                scored.append((node, score))
        scored.sort(key=lambda pair: -pair[1])
        return scored[:k]

    def retrieve(self, question: str, k: int = 6) -> list[tuple[models.KnowledgeNode, float]]:
        """混合检索：向量检索优先，关键词补充。"""
        result: list[tuple[models.KnowledgeNode, float]] = []
        seen: set[str] = set()

        for hit in embedding_service.semantic_search(self.db, question, k):
            node = self.db.get(models.KnowledgeNode, hit["id"])
            if node is not None and node.id not in seen:
                result.append((node, hit["score"]))
                seen.add(node.id)

        if len(result) < k:
            for node, score in self._keyword_search(question, k):
                if node.id not in seen and len(result) < k:
                    result.append((node, min(score, 1.0) * 0.5))
                    seen.add(node.id)
        return result[:k]

    def query(self, question: str) -> dict:
        hits = self.retrieve(question)
        retrieved = [
            {
                "id": n.id,
                "name": n.name,
                "category": n.category,
                "score": round(s, 4),
                "source_url": n.source_url,
            }
            for n, s in hits
        ]

        if not hits:
            return {
                "question": question,
                "status": "no_context",
                "message": "未在知识库中找到相关资料，无法给出有依据的回答。",
                "answer": None,
                "retrieved": [],
                "context": None,
            }

        context = "\n".join(
            f"[{i + 1}] {n.name} ({n.category}) — {n.description}"
            for i, (n, _s) in enumerate(hits)
        )

        client = LLMClient()
        if not client.configured:
            return {
                "question": question,
                "status": "retrieval_ready_no_llm",
                "message": (
                    "已检索到相关知识节点，但未配置 LLM（请设置 LLM_API_BASE / LLM_API_KEY / LLM_MODEL），"
                    "当前仅返回检索结果。"
                ),
                "answer": None,
                "retrieved": retrieved,
                "context": context,
            }

        user_prompt = (
            f"Numbered knowledge-node context:\n{context}\n\n"
            f"Question: {question}\n\n"
            f"Answer with inline citations [n] referencing the numbered context:"
        )
        try:
            answer = client.chat(SYSTEM_PROMPT, user_prompt)
        except LLMError as exc:
            return {
                "question": question,
                "status": "error",
                "message": f"LLM 调用失败：{exc}",
                "answer": None,
                "retrieved": retrieved,
                "context": context,
            }

        return {
            "question": question,
            "status": "grounded",
            "message": "回答已由检索到的知识节点生成（可追溯来源）。",
            "answer": answer,
            "retrieved": retrieved,
            "context": context,
        }
