"""RAG 查询层接口（Phase 6 目标）。

当前阶段（Phase 0/1）只实现「检索」步骤，用于验证数据链路；
Phase 5 将把关键词检索替换为 embedding + 向量检索，
Phase 6 将接入 LLM 生成 grounded answer。
"""
from __future__ import annotations

import re

from sqlalchemy.orm import Session

from .. import models

STOPWORDS = {
    "the", "and", "for", "are", "was", "were", "what", "how", "why", "when",
    "where", "which", "who", "this", "that", "with", "from", "into", "about",
    "between", "does", "should", "would", "could", "can", "not", "your", "you",
    "its", "they", "them", "their", "there", "here", "has", "have", "had", "been",
    "being", "will", "shall", "may", "might", "must", "some", "such", "than",
    "then", "also", "but", "get", "got", "use", "used", "using", "like", "just",
    "via", "per", "etc", "relation", "related", "relationship", "explain",
    "describe", "difference", "compare", "tell",
}


class RAGService:
    def __init__(self, db: Session):
        self.db = db

    def retrieve(self, question: str, k: int = 6) -> list[tuple[models.KnowledgeNode, float]]:
        """检索阶段：对节点做关键词加权匹配（临时实现，后续替换为向量检索）。"""
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

    def query(self, question: str) -> dict:
        hits = self.retrieve(question)
        retrieved = [
            {"id": n.id, "name": n.name, "category": n.category, "score": round(s, 2)}
            for n, s in hits
        ]
        context = (
            "\n".join(f"[{n.name} ({n.category})] {n.description}" for n, _ in hits)
            if hits
            else None
        )
        return {
            "question": question,
            "status": "retrieval_ready_no_llm",
            "message": (
                "RAG 检索层已运行（关键词检索）；LLM / Embedding 尚未接入（计划于 Phase 5/6）。"
            ),
            "answer": None,
            "retrieved": retrieved,
            "context": context,
        }
