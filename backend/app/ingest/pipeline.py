"""数据接入 pipeline（Phase 4）。

流程：拉取 → 清洗 → 分类映射 → 去重 → 实体链接 / 关系抽取 → 幂等写入 → 记录运行。

去重策略：先按 slug 命中已有节点，再按名称（大小写不敏感）对齐；
命中则「更新描述与来源」（保留 id / name / popularity / 已有关系，不破坏旧数据），
否则「插入新节点」。关系抽取使用 Wikipedia 内部链接与已有节点的实体对齐，生成
`related_to` 关系（真实来源，不伪造语义）。
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from .. import models
from . import wikipedia

CATEGORY_RULES: list[tuple[str, str]] = [
    ("architecture", "architecture"),
    ("algorithm", "algorithm"),
    ("dataset", "dataset"),
    ("natural language processing", "field"),
    ("computer vision", "field"),
    ("reinforcement learning", "field"),
    ("deep learning", "field"),
    ("machine learning", "field"),
    ("model", "model"),
    ("task", "task"),
    ("technique", "technique"),
    ("method", "technique"),
    ("application", "application"),
    ("neural network", "architecture"),
]


def map_category(categories: list[str]) -> str:
    text = " ".join(categories).lower()
    for needle, cat in CATEGORY_RULES:
        if needle in text:
            return cat
    return "concept"


def _find_node(db: Session, title: str) -> models.KnowledgeNode | None:
    """按 slug / 名称对齐到已有节点。"""
    slug = wikipedia.slugify(title)
    node = db.get(models.KnowledgeNode, slug)
    if node is not None:
        return node
    return (
        db.query(models.KnowledgeNode)
        .filter(models.KnowledgeNode.name.ilike(title.strip()))
        .first()
    )


def _link_relations(
    db: Session, node_id: str, link_titles: list[str], limit: int
) -> int:
    """实体链接：把 Wikipedia 内部链接对齐到已有节点，生成 related_to 关系。"""
    created = 0
    for lt in link_titles:
        if created >= limit:
            break
        if wikipedia.slugify(lt) == node_id:
            continue
        target = _find_node(db, lt)
        if target is None or target.id == node_id:
            continue
        exists = (
            db.query(models.KnowledgeRelation)
            .filter_by(source_id=node_id, target_id=target.id, relation_type="related_to")
            .first()
        )
        reverse = (
            db.query(models.KnowledgeRelation)
            .filter_by(source_id=target.id, target_id=node_id, relation_type="related_to")
            .first()
        )
        if exists or reverse:
            continue
        db.add(
            models.KnowledgeRelation(
                source_id=node_id, target_id=target.id, relation_type="related_to"
            )
        )
        created += 1
    if created:
        db.commit()
    return created


def run_wikipedia_ingestion(
    db: Session,
    titles: list[str],
    max_relations: int = 20,
) -> dict:
    """执行一轮 Wikipedia ingestion，幂等且可重复运行。返回运行统计 dict。"""
    run = models.IngestionRun(source="wikipedia", status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    fetched = inserted = updated = skipped = relations_created = 0
    notes: list[str] = []

    for raw_title in titles:
        title = raw_title.strip()
        if not title:
            continue
        try:
            summary = wikipedia.fetch_summary(title)
        except Exception as exc:  # noqa: BLE001 —— 网络/解析异常不应中断整轮
            skipped += 1
            notes.append(f"{title}: fetch failed ({exc.__class__.__name__})")
            continue

        if not summary["extract"]:
            skipped += 1
            notes.append(f"{title}: no extract")
            continue

        fetched += 1
        slug = wikipedia.slugify(summary["title"])
        node = _find_node(db, summary["title"])

        if node is None:
            try:
                cats, _ = wikipedia.fetch_categories_links(summary["title"])
            except Exception:
                cats = []
            node = models.KnowledgeNode(
                id=slug,
                name=summary["title"],
                category=map_category(cats),
                description=summary["extract"],
                source="Wikipedia",
                source_url=summary["url"],
                popularity=0.0,
            )
            db.add(node)
            db.commit()
            inserted += 1
        else:
            # 更新（保留 id / name / popularity 与已有关系，不破坏旧数据）
            node.description = summary["extract"] or node.description
            node.source = "Wikipedia"
            node.source_url = summary["url"] or node.source_url
            db.commit()
            updated += 1

        if max_relations > 0:
            try:
                _, links = wikipedia.fetch_categories_links(summary["title"])
                relations_created += _link_relations(db, node.id, links, max_relations)
            except Exception:
                pass

    if skipped == len(titles) and fetched == 0:
        status = "failed"
    elif skipped > 0:
        status = "partial"
    else:
        status = "completed"

    run.status = status
    run.fetched = fetched
    run.inserted = inserted
    run.updated = updated
    run.skipped = skipped
    run.relations_created = relations_created
    run.finished_at = datetime.utcnow()
    run.message = "; ".join(notes) or None
    db.commit()

    return {
        "run_id": run.id,
        "source": run.source,
        "status": status,
        "fetched": fetched,
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
        "relations_created": relations_created,
        "message": run.message or "",
    }
