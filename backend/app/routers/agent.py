from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.agent import AgentService

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/query", response_model=schemas.AgentResult)
def agent_query(payload: schemas.AgentQueryIn, db: Session = Depends(get_db)):
    """运行 Agent：多步工具调用探索知识库，返回答案 + 执行轨迹 + 依据。"""
    return AgentService(db).run(payload.question, max_steps=payload.max_steps)


@router.get("/runs", response_model=list[schemas.AgentRunOut])
def agent_runs(db: Session = Depends(get_db)):
    """最近的 Agent 执行记录。"""
    return db.query(models.AgentRun).order_by(models.AgentRun.id.desc()).limit(50).all()


@router.get("/tools", response_model=list[schemas.AgentToolInfo])
def agent_tools():
    """列出 Agent 可用工具及其参数。"""
    return AgentService.tool_infos()
