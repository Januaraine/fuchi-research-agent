from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
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
