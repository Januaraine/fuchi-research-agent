from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services import embedding_service

router = APIRouter(prefix="/api/semantic", tags=["semantic"])


@router.post("/build", response_model=schemas.SemanticBuildOut)
def build_index(db: Session = Depends(get_db)):
    result = embedding_service.build_embeddings(db)
    return schemas.SemanticBuildOut(**result, status="built")


@router.get("/search", response_model=schemas.SemanticSearchOut)
def semantic_search(q: str, limit: int = 10, db: Session = Depends(get_db)):
    hits = embedding_service.semantic_search(db, q, min(max(1, limit), 50))
    return schemas.SemanticSearchOut(query=q, hits=hits)


@router.get("/recommend/{node_id}", response_model=schemas.RecommendOut)
def semantic_recommend(node_id: str, limit: int = 10, db: Session = Depends(get_db)):
    node = db.get(models.KnowledgeNode, node_id)
    if node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    recs = embedding_service.recommend(db, node_id, min(max(1, limit), 50))
    return schemas.RecommendOut(node_id=node_id, node_name=node.name, recommendations=recs)


@router.get("/compare", response_model=schemas.SemanticCompareOut)
def compare(q: str, limit: int = 10, db: Session = Depends(get_db)):
    """对比：关键词检索（字面匹配） vs 语义检索（向量相似度）。"""
    cap = min(max(1, limit), 50)
    like = f"%{q}%"
    kw_nodes = (
        db.query(models.KnowledgeNode)
        .filter(
            or_(
                models.KnowledgeNode.name.ilike(like),
                models.KnowledgeNode.description.ilike(like),
                models.KnowledgeNode.category.ilike(like),
            )
        )
        .limit(cap)
        .all()
    )
    keyword = [
        {"id": n.id, "name": n.name, "category": n.category, "score": 1.0} for n in kw_nodes
    ]
    semantic = embedding_service.semantic_search(db, q, cap)
    return schemas.SemanticCompareOut(query=q, keyword=keyword, semantic=semantic)
