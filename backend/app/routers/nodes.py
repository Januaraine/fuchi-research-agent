from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/nodes", tags=["nodes"])


def _name_maps(db: Session):
    nodes = db.query(models.KnowledgeNode).all()
    names = {n.id: n.name for n in nodes}
    cats = {n.id: n.category for n in nodes}
    return names, cats


@router.get("", response_model=list[schemas.NodeSummary])
def list_nodes(
    category: str | None = None,
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(models.KnowledgeNode)
    if category:
        query = query.filter(models.KnowledgeNode.category == category)
    if q:
        query = query.filter(models.KnowledgeNode.name.ilike(f"%{q}%"))
    return (
        query.order_by(models.KnowledgeNode.name)
        .offset(offset)
        .limit(min(limit, 200))
        .all()
    )


@router.get("/{node_id}", response_model=schemas.NodeDetail)
def get_node(node_id: str, db: Session = Depends(get_db)):
    node = db.get(models.KnowledgeNode, node_id)
    if node is None:
        raise HTTPException(status_code=404, detail="Node not found")

    names, cats = _name_maps(db)
    outgoing_rel = db.query(models.KnowledgeRelation).filter_by(source_id=node_id).all()
    incoming_rel = db.query(models.KnowledgeRelation).filter_by(target_id=node_id).all()

    def to_rel(r: models.KnowledgeRelation) -> schemas.RelationOut:
        return schemas.RelationOut(
            id=r.id,
            source_id=r.source_id,
            target_id=r.target_id,
            relation_type=r.relation_type,
            source_name=names.get(r.source_id),
            source_category=cats.get(r.source_id),
            target_name=names.get(r.target_id),
            target_category=cats.get(r.target_id),
        )

    outgoing = [to_rel(r) for r in outgoing_rel]
    incoming = [to_rel(r) for r in incoming_rel]

    neighbor_ids = {r.target_id for r in outgoing_rel} | {r.source_id for r in incoming_rel}
    neighbor_ids.discard(node_id)
    related_nodes = (
        db.query(models.KnowledgeNode)
        .filter(models.KnowledgeNode.id.in_(neighbor_ids))
        .all()
        if neighbor_ids
        else []
    )

    detail = schemas.NodeDetail.model_validate(node)
    detail.outgoing = outgoing
    detail.incoming = incoming
    detail.related = [schemas.NodeSummary.model_validate(n) for n in related_nodes]
    return detail
