"""Seed 数据加载。"""
from sqlalchemy.orm import Session

from . import models
from .seed_data import NODES, RELATIONS


def seed_db(db: Session) -> dict:
    """若库为空则导入 Seed Data；否则跳过。返回导入统计。"""
    if db.query(models.KnowledgeNode).count() > 0:
        return {"nodes": 0, "relations": 0, "skipped": True}

    nodes: dict[str, models.KnowledgeNode] = {}
    for n in NODES:
        nodes[n[0]] = models.KnowledgeNode(
            id=n[0], name=n[1], category=n[2], description=n[3], source=n[4], source_url=n[5]
        )
    db.add_all(nodes.values())
    db.flush()

    relations: list[models.KnowledgeRelation] = []
    seen: set[tuple[str, str, str]] = set()
    for r in RELATIONS:
        key = (r[0], r[1], r[2])
        if key in seen:
            continue
        seen.add(key)
        relations.append(
            models.KnowledgeRelation(source_id=r[0], target_id=r[1], relation_type=r[2])
        )
    db.add_all(relations)
    db.commit()
    return {"nodes": len(nodes), "relations": len(relations), "skipped": False}


if __name__ == "__main__":
    from .database import Base, SessionLocal, engine

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        result = seed_db(db)
    print("Seed result:", result)
