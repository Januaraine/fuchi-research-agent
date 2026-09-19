import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ORIGINS
from .database import Base, SessionLocal, engine
from .routers import agent, graph, ingest, nodes, rag, realtime, search, semantic, stats
from .seed import seed_db
from .services import embedding_service
from .services.realtime import realtime_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_db(db)
        embedding_service.ensure_embeddings(db)
    loop_task = asyncio.create_task(realtime_loop())
    yield
    loop_task.cancel()
    try:
        await loop_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Knowledge Observatory API",
    description="未来文明知识观测站 —— 真实世界知识（AI/ML）的知识图与检索 API。",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stats.router)
app.include_router(nodes.router)
app.include_router(graph.router)
app.include_router(search.router)
app.include_router(rag.router)
app.include_router(realtime.router)
app.include_router(ingest.router)
app.include_router(semantic.router)
app.include_router(agent.router)


@app.get("/")
def root():
    return {
        "name": "Knowledge Observatory",
        "docs": "/docs",
        "endpoints": [
            "/api/health",
            "/api/stats",
            "/api/nodes",
            "/api/graph",
            "/api/graph/neighbors/{node_id}",
            "/api/search",
            "/api/rag/query",
            "/api/realtime/history",
            "/api/ingest/wikipedia",
            "/api/ingest/runs",
            "/api/semantic/search",
            "/api/semantic/compare",
            "/api/semantic/recommend/{node_id}",
            "/api/agent/query",
            "/api/agent/runs",
            "/api/agent/tools",
            "WS /api/ws",
        ],
    }
