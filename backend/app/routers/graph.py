from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("", response_model=schemas.GraphOut)
def get_graph(node_id: str | None = None, depth: int = 1, db: Session = Depends(get_db)):
    if node_id:
        visited: set[str] = set()
        frontier = {node_id}
        for _ in range(max(1, depth) + 1):
            visited |= frontier
            neighbors: set[str] = set()
            for nid in frontier:
                out = {r.target_id for r in db.query(models.KnowledgeRelation).filter_by(source_id=nid)}
                inc = {r.source_id for r in db.query(models.KnowledgeRelation).filter_by(target_id=nid)}
                neighbors |= out | inc
            frontier = neighbors - visited
        nodes = db.query(models.KnowledgeNode).filter(models.KnowledgeNode.id.in_(visited)).all()
        edges = db.query(models.KnowledgeRelation).filter(
            models.KnowledgeRelation.source_id.in_(visited),
            models.KnowledgeRelation.target_id.in_(visited),
        ).all()
    else:
        nodes = db.query(models.KnowledgeNode).all()
        edges = db.query(models.KnowledgeRelation).all()

    return schemas.GraphOut(
        nodes=[schemas.GraphNode(id=n.id, name=n.name, category=n.category) for n in nodes],
        edges=[
            schemas.GraphEdge(source=e.source_id, target=e.target_id, relation_type=e.relation_type)
            for e in edges
        ],
    )
