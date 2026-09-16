from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services.rag_service import RAGService

router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.post("/query", response_model=schemas.RagQueryOut)
def rag_query(payload: schemas.RagQueryIn, db: Session = Depends(get_db)):
    return RAGService(db).query(payload.question)
