from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..ingest.pipeline import run_wikipedia_ingestion

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


@router.post("/wikipedia", response_model=schemas.IngestResult)
def ingest_wikipedia(payload: schemas.IngestWikipediaIn, db: Session = Depends(get_db)):
    """触发一轮 Wikipedia 数据接入（同步执行，幂等可重复）。"""
    return run_wikipedia_ingestion(db, payload.titles, max_relations=payload.max_relations)


@router.get("/runs", response_model=list[schemas.IngestionRunOut])
def list_runs(db: Session = Depends(get_db)):
    """最近的 ingestion 运行记录。"""
    return (
        db.query(models.IngestionRun)
        .order_by(models.IngestionRun.id.desc())
        .limit(50)
        .all()
    )
