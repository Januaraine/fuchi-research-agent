from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class KnowledgeNode(Base):
    """知识节点：真实世界知识的最小单位。"""

    __tablename__ = "knowledge_nodes"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # slug，例如 "transformer"
    name: Mapped[str] = mapped_column(String, index=True)
    category: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String, nullable=True)
    popularity: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class KnowledgeRelation(Base):
    """知识关系：连接两个知识节点的有向边。"""

    __tablename__ = "knowledge_relations"
    __table_args__ = (
        UniqueConstraint("source_id", "target_id", "relation_type", name="uq_relation"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("knowledge_nodes.id"), index=True)
    target_id: Mapped[str] = mapped_column(ForeignKey("knowledge_nodes.id"), index=True)
    relation_type: Mapped[str] = mapped_column(String, index=True)


class IngestionRun(Base):
    """数据接入运行记录：记录一次 ingestion pipeline 的源、结果与统计。"""

    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String, index=True)  # 例如 "wikipedia"
    status: Mapped[str] = mapped_column(String)  # completed | partial | failed
    fetched: Mapped[int] = mapped_column(Integer, default=0)
    inserted: Mapped[int] = mapped_column(Integer, default=0)
    updated: Mapped[int] = mapped_column(Integer, default=0)
    skipped: Mapped[int] = mapped_column(Integer, default=0)
    relations_created: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class NodeEmbedding(Base):
    """知识节点向量（Phase 5）：TF-IDF n-gram 向量，L2 归一化后持久化。"""

    __tablename__ = "node_embeddings"

    node_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_nodes.id"), primary_key=True
    )
    model: Mapped[str] = mapped_column(String)  # 例如 "tfidf-ngram-v1"
    vector_json: Mapped[str] = mapped_column(Text)  # {"token": weight, ...}
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SemanticIndexMeta(Base):
    """语义索引元信息：记录模型版本、词表 IDF 与构建规模（用于判重/重建）。"""

    __tablename__ = "semantic_index_meta"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model: Mapped[str] = mapped_column(String)
    num_nodes: Mapped[int] = mapped_column(Integer, default=0)
    idf_json: Mapped[str] = mapped_column(Text)  # {"token": idf, ...}
    built_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AgentRun(Base):
    """Agent 执行记录：记录一次 Agent 的多步工具调用轨迹与最终结论。"""

    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String)  # completed | no_llm | error
    llm_used: Mapped[bool] = mapped_column(Boolean, default=False)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    steps_json: Mapped[str] = mapped_column(Text, default="[]")  # [{"step","action","args","observation"}]
    evidence_json: Mapped[str] = mapped_column(Text, default="[]")  # [{"id","name","category","source_url"}]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
