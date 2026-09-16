from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "knowledge-observatory"}


@router.get("/stats", response_model=schemas.StatsOut)
def stats(db: Session = Depends(get_db)):
    nodes = db.query(models.KnowledgeNode).count()
    relations = db.query(models.KnowledgeRelation).count()
    counter = Counter(n.category for n in db.query(models.KnowledgeNode.category).all())
    return schemas.StatsOut(nodes=nodes, relations=relations, categories=dict(counter))


@router.get("/categories", response_model=list[dict])
def categories(db: Session = Depends(get_db)):
    counter = Counter(n.category for n in db.query(models.KnowledgeNode.category).all())
    return [{"category": k, "count": v} for k, v in sorted(counter.items())]
