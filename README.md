# Knowledge Observatory · 知识观测站

> 一个以 **OC 世界观为视觉与叙事外壳**、以 **真实世界知识为核心数据** 的未来文明知识观测与交互系统。

本项目当前完成 **Phase 0（项目基础）+ Phase 1（Seed Data）**，并附带基础知识图谱可视化与 RAG 查询层接口（暂未接入 LLM）。

---

## 架构

```text
Frontend (Next.js + TS)
        │  REST (fetch)
        ▼
Backend (FastAPI)
        │
        ▼
SQLite (SQLAlchemy)  ← 119 个真实 AI/ML 知识节点 · 235 条关系
```

- 前端：`frontend/`（Next.js App Router + TypeScript，OC「未来文明观测站」暗色主题）
- 后端：`backend/`（FastAPI + SQLAlchemy 2 + SQLite）
- 数据：`backend/app/seed_data.py`（真实 AI/ML 知识，来源 Wikipedia / arXiv）

## 目录结构

```text
backend/
  app/
    main.py            # FastAPI 应用 + CORS + 启动时自动建表/seed
    models.py          # KnowledgeNode / KnowledgeRelation
    schemas.py         # Pydantic 响应模型
    seed_data.py       # Seed Data（119 节点 / 235 关系）
    seed.py            # 数据导入（幂等：库非空则跳过）
    routers/           # nodes / graph / search / stats / rag
    services/rag_service.py   # RAG 查询层接口（检索已实现，LLM 留待 Phase 5/6）
  requirements.txt
frontend/
  app/                 # page.tsx(Dashboard) · graph/page.tsx · nodes/[id]/page.tsx
  components/          # Navbar · GraphCanvas(力导向图) · NodeCard · RelationList · StatCard
  lib/                 # api.ts · types.ts · colors.ts
```

## 运行

### 1. 后端（端口 8000）

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

首次启动会自动建表并导入 Seed Data（无需手动 seed）。API 文档：http://localhost:8000/docs

> 说明：仓库里若存在 `backend/.deps/`，是开发时沙箱环境下的临时安装目录，正常本地开发请用上面的 `.venv` 方式，`.deps` 可安全删除（已被 `.gitignore` 忽略）。

### 2. 前端（端口 3000）

```bash
cd frontend
npm install
npm run dev
```

打开 http://localhost:3000 。前端默认请求 `http://127.0.0.1:8000`，可通过环境变量覆盖：

```bash
NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000 npm run dev
```

## API

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 健康检查 |
| GET | `/api/stats` | 节点/关系总数 + 分类统计 |
| GET | `/api/categories` | 分类列表 |
| GET | `/api/nodes` | 节点列表（`?category=` `?q=` `?limit=` `?offset=`） |
| GET | `/api/nodes/{id}` | 节点详情（含出/入关系 + 相关节点） |
| GET | `/api/graph` | 全图节点+边（`?node_id=&depth=` 返回邻域子图） |
| GET | `/api/search?q=` | 关键词搜索（名称/描述/分类） |
| POST | `/api/rag/query` | RAG 查询（当前为检索层预览，`status=retrieval_ready_no_llm`） |

## 数据模型

`KnowledgeNode`：`id · name · category · description · source · source_url · popularity · created_at · updated_at`

`KnowledgeRelation`：`source_id → target_id`，`relation_type ∈ { subfield_of, is_a, part_of, used_in, based_on, related_to }`

分类：`field / paradigm / algorithm / model / architecture / technique / concept / task / dataset / application`

## 开发阶段进度

- [x] **Phase 0** — 项目基础（前后端骨架、数据库、完整数据链路 `Frontend → Backend → DB`）
- [x] **Phase 1** — Seed Data（119 真实节点 / 235 关系，可查询可持久化）
- [x] 基础 Knowledge Graph 可视化 + 搜索 + 节点详情（Phase 2 的雏形）
- [ ] Phase 2 — 完整图导航（聚焦 / 展开 / 关系筛选）
- [ ] Phase 3 — 实时系统（WebSocket / SSE）
- [ ] Phase 4 — 真实数据源接入（Wikipedia/Wikidata 等 ingestion pipeline）
- [ ] Phase 5 — 语义搜索（Embedding + 向量库）
- [ ] Phase 6 — RAG（接入 LLM，生成 grounded answer）
- [ ] Phase 7 — Agent（Tool Calling / 多步推理）

## 关于 RAG 接口（留接口阶段）

`backend/app/services/rag_service.py` 已定义查询层接口：

```text
User Question → 检索(关键词匹配) → Retrieve Sources → [Phase 6: LLM] → Grounded Answer
```

当前 `retrieve()` 使用关键词加权匹配（临时实现），`query()` 返回检索到的节点与上下文，
`answer` 字段为 `None`。Phase 5 将替换为 embedding + 向量检索，Phase 6 接入 LLM。
