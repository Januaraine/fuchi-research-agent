from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ORIGINS
from .database import Base, SessionLocal, engine
from .routers import graph, nodes, rag, search, stats
from .seed import seed_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_db(db)
    yield


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


@app.get("/")
def root():
    return {
        "name": "Knowledge Observatory",
        "docs": "/docs",
        "endpoints": ["/api/health", "/api/stats", "/api/nodes", "/api/graph", "/api/search", "/api/rag/query"],
    }
