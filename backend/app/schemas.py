from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NodeSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    category: str
    description: str
    source: Optional[str] = None
    source_url: Optional[str] = None
    popularity: float = 0.0


class RelationOut(BaseModel):
    id: int
    source_id: str
    target_id: str
    relation_type: str
    # 关联节点的冗余信息，便于前端直接渲染
    source_name: Optional[str] = None
    source_category: Optional[str] = None
    target_name: Optional[str] = None
    target_category: Optional[str] = None


class NodeDetail(NodeSummary):
    outgoing: list[RelationOut] = []
    incoming: list[RelationOut] = []
    related: list[NodeSummary] = []


class GraphNode(BaseModel):
    id: str
    name: str
    category: str


class GraphEdge(BaseModel):
    source: str
    target: str
    relation_type: str


class GraphOut(BaseModel):
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []


class StatsOut(BaseModel):
    nodes: int
    relations: int
    categories: dict[str, int]


class RagQueryIn(BaseModel):
    question: str


class RagSource(BaseModel):
    id: str
    name: str
    category: str
    score: float
    source_url: Optional[str] = None


class RagQueryOut(BaseModel):
    question: str
    status: str  # "grounded" | "no_context" | "retrieval_ready_no_llm" | "error"
    message: str
    answer: Optional[str] = None
    retrieved: list[RagSource] = []
    context: Optional[str] = None


class IngestWikipediaIn(BaseModel):
    titles: list[str]
    max_relations: int = 20  # 每个页面最多建立的实体链接关系数


class IngestResult(BaseModel):
    run_id: int
    source: str
    status: str
    fetched: int
    inserted: int
    updated: int
    skipped: int
    relations_created: int
    message: str


class IngestionRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    status: str
    fetched: int
    inserted: int
    updated: int
    skipped: int
    relations_created: int
    message: Optional[str] = None
    started_at: datetime
    finished_at: Optional[datetime] = None


class SemanticHit(BaseModel):
    id: str
    name: str
    category: str
    score: float


class SemanticSearchOut(BaseModel):
    query: str
    hits: list[SemanticHit] = []


class SemanticCompareOut(BaseModel):
    query: str
    keyword: list[SemanticHit] = []
    semantic: list[SemanticHit] = []


class SemanticBuildOut(BaseModel):
    built: int
    model: str
    vocab_size: int
    status: str


class RecommendOut(BaseModel):
    node_id: str
    node_name: str
    recommendations: list[SemanticHit] = []


class AgentQueryIn(BaseModel):
    question: str
    max_steps: int = 6


class AgentStep(BaseModel):
    step: int
    action: str
    args: dict = {}
    observation: str = ""


class AgentEvidence(BaseModel):
    id: str
    name: str
    category: str
    source_url: Optional[str] = None


class AgentResult(BaseModel):
    run_id: int
    question: str
    status: str  # completed | no_llm | error
    llm_used: bool
    answer: str
    steps: list[AgentStep] = []
    evidence: list[AgentEvidence] = []


class AgentRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question: str
    status: str
    llm_used: bool
    answer: Optional[str] = None
    steps_json: str
    evidence_json: str
    created_at: datetime


class AgentToolInfo(BaseModel):
    name: str
    description: str
    params: dict
