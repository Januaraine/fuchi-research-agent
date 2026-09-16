from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=list[schemas.NodeSummary])
def search(q: str, limit: int = 20, db: Session = Depends(get_db)):
    like = f"%{q}%"
    return (
        db.query(models.KnowledgeNode)
        .filter(
            or_(
                models.KnowledgeNode.name.ilike(like),
                models.KnowledgeNode.description.ilike(like),
                models.KnowledgeNode.category.ilike(like),
            )
        )
        .order_by(models.KnowledgeNode.name)
        .limit(min(limit, 50))
        .all()
    )
