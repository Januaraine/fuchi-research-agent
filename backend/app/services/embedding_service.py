"""语义检索 / 向量检索（Phase 5）。

轻量、无外部依赖的实现：对知识节点的 `name + description + category` 构建
**TF-IDF（词 + 字符 3-gram）向量**，L2 归一化后持久化到 `node_embeddings` 表，
检索用**余弦相似度**（归一化后即点积）。

选择说明：
- 不依赖外部 LLM / 向量数据库，纯标准库即可跑通「生成 Embedding → 持久化 →
  向量检索 → 相似度推荐」的完整链路，符合「不堆技术」原则；
- 向量化接口与检索解耦，后续 Phase 6/7 可无缝替换为神经 embedding / 向量库。
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter

from sqlalchemy.orm import Session

from .. import models

MODEL = "tfidf-ngram-v1"

STOPWORDS = {
    "the", "and", "for", "are", "was", "were", "what", "how", "why", "when",
    "where", "which", "who", "this", "that", "with", "from", "into", "about",
    "between", "does", "should", "would", "could", "can", "not", "your", "you",
    "its", "they", "them", "their", "there", "here", "has", "have", "had",
    "been", "being", "will", "shall", "may", "might", "must", "some", "such",
    "than", "then", "also", "but", "get", "got", "use", "used", "using",
    "like", "just", "via", "per", "etc", "more", "most", "one", "two", "new",
    "based", "based_on", "enables", "enable", "models", "model", "data",
    "learn", "learning", "system", "systems", "often", "typically", "known",
}


def _features(text: str) -> list[str]:
    """词 + 字符 3-gram 特征（用于形态鲁棒的部分匹配）。"""
    words = re.findall(r"[a-z0-9]+", text.lower())
    feats: list[str] = []
    for w in words:
        if w in STOPWORDS or len(w) < 2:
            continue
        feats.append(w)
        if len(w) >= 4:
            feats.extend(w[i : i + 3] for i in range(len(w) - 2))
    return feats


def _doc_text(node: models.KnowledgeNode) -> str:
    return f"{node.name} {node.description} {node.category}"


def _tf_vector(features: list[str], idf: dict[str, float]) -> dict[str, float]:
    """TF-IDF 加权 + L2 归一化，返回稀疏向量 dict。"""
    counts = Counter(features)
    total = sum(counts.values()) or 1
    raw: dict[str, float] = {}
    for tok, c in counts.items():
        raw[tok] = (c / total) * idf.get(tok, 1.0)
    norm = math.sqrt(sum(v * v for v in raw.values())) or 1.0
    return {tok: v / norm for tok, v in raw.items()}


def build_embeddings(db: Session) -> dict:
    """重建全部节点向量与词表 IDF。返回统计 dict。"""
    nodes = db.query(models.KnowledgeNode).all()

    df: Counter[str] = Counter()
    docs: list[tuple[models.KnowledgeNode, list[str]]] = []
    for n in nodes:
        feats = _features(_doc_text(n))
        docs.append((n, feats))
        df.update(set(feats))  # 文档频率按「去重后 token」计

    N = max(1, len(nodes))
    idf = {tok: math.log((1 + N) / (1 + df[tok])) + 1.0 for tok in df}

    db.query(models.NodeEmbedding).delete()
    for n, feats in docs:
        vec = _tf_vector(feats, idf)
        db.add(
            models.NodeEmbedding(
                node_id=n.id, model=MODEL, vector_json=json.dumps(vec, separators=(",", ":"))
            )
        )

    db.query(models.SemanticIndexMeta).delete()
    db.add(
        models.SemanticIndexMeta(
            model=MODEL, num_nodes=len(nodes), idf_json=json.dumps(idf, separators=(",", ":"))
        )
    )
    db.commit()
    return {"built": len(nodes), "model": MODEL, "vocab_size": len(idf)}


def ensure_embeddings(db: Session) -> bool:
    """索引缺失 / 过期时重建。返回是否发生了重建。"""
    node_count = db.query(models.KnowledgeNode).count()
    emb_count = db.query(models.NodeEmbedding).count()
    meta = db.query(models.SemanticIndexMeta).order_by(models.SemanticIndexMeta.id.desc()).first()
    if meta is None or meta.model != MODEL or meta.num_nodes != node_count or emb_count != node_count:
        build_embeddings(db)
        return True
    return False


def _load_idf(db: Session) -> dict[str, float]:
    meta = db.query(models.SemanticIndexMeta).order_by(models.SemanticIndexMeta.id.desc()).first()
    if meta is None:
        return {}
    return json.loads(meta.idf_json)


def _hit(node_id: str, score: float, db: Session) -> dict | None:
    node = db.get(models.KnowledgeNode, node_id)
    if node is None:
        return None
    return {"id": node.id, "name": node.name, "category": node.category, "score": round(score, 4)}


def semantic_search(db: Session, query: str, limit: int = 10) -> list[dict]:
    """自然语言查询 → 语义相关节点（余弦相似度）。"""
    ensure_embeddings(db)
    idf = _load_idf(db)
    qvec = _tf_vector(_features(query), idf)
    if not qvec:
        return []

    scored: list[dict] = []
    for emb in db.query(models.NodeEmbedding).all():
        v = json.loads(emb.vector_json)
        dot = sum(qvec[t] * v.get(t, 0.0) for t in qvec)
        if dot > 0:
            hit = _hit(emb.node_id, dot, db)
            if hit:
                scored.append(hit)
    scored.sort(key=lambda x: -x["score"])
    return scored[: max(1, limit)]


def recommend(db: Session, node_id: str, limit: int = 10) -> list[dict]:
    """基于语义相似度的知识推荐（排除自身）。"""
    ensure_embeddings(db)
    emb = db.get(models.NodeEmbedding, node_id)
    if emb is None:
        return []
    v = json.loads(emb.vector_json)

    scored: list[dict] = []
    others = (
        db.query(models.NodeEmbedding)
        .filter(models.NodeEmbedding.node_id != node_id)
        .all()
    )
    for other in others:
        ov = json.loads(other.vector_json)
        dot = sum(v[t] * ov.get(t, 0.0) for t in v)
        if dot > 0:
            hit = _hit(other.node_id, dot, db)
            if hit:
                scored.append(hit)
    scored.sort(key=lambda x: -x["score"])
    return scored[: max(1, limit)]
