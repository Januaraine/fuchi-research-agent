# Knowledge Observatory · 知识观测站

> 一个以 **OC 世界观为视觉与叙事外壳**、以 **真实世界知识为核心数据** 的未来文明知识观测与交互系统。

本项目当前完成 **Phase 0（项目基础）+ Phase 1（Seed Data）+ Phase 2（知识图谱）+ Phase 3（实时系统）+ Phase 4（真实数据接入）**，并附带 RAG 查询层接口（暂未接入 LLM）。

---

## 架构

```text
Frontend (Next.js + TS)
        │  REST (fetch) + WebSocket
        ▼
Backend (FastAPI)
        │
        ▼
SQLite (SQLAlchemy)  ← 119 个真实 AI/ML 知识节点 · 235 条关系（Seed）
                     ← 可经 Wikipedia ingestion pipeline 持续扩充
```

- 前端：`frontend/`（Next.js App Router + TypeScript，OC「未来文明观测站」暗色主题）
- 后端：`backend/`（FastAPI + SQLAlchemy 2 + SQLite）
- 数据：`backend/app/seed_data.py`（真实 AI/ML 知识，来源 Wikipedia / arXiv）
- 数据接入：`backend/app/ingest/`（Wikipedia 拉取 → 清洗 → 去重 → 实体链接 → 关系抽取 → 幂等写入）

## 目录结构

```text
backend/
  app/
    main.py            # FastAPI 应用 + CORS + 启动时自动建表/seed
    models.py          # KnowledgeNode / KnowledgeRelation / IngestionRun
    schemas.py         # Pydantic 响应模型
    seed_data.py       # Seed Data（119 节点 / 235 关系）
    seed.py            # 数据导入（幂等：库非空则跳过）
    ingest/            # 数据接入 pipeline（wikipedia 适配器 + 去重/实体链接 + CLI）
    routers/           # nodes / graph / search / stats / rag / realtime / ingest
    services/rag_service.py   # RAG 查询层接口（检索已实现，LLM 留待 Phase 5/6）
    services/realtime.py      # WebSocket 连接管理 + 后台事件循环（模拟系统动态）
  requirements.txt
frontend/
  app/                 # page.tsx(Dashboard) · graph/page.tsx · nodes/[id]/page.tsx
  components/          # Navbar · GraphCanvas(力导向图) · NodeCard · RelationList · StatCard
                       # ActivityFeed(实时活动流) · TrendingPanel(实时趋势榜)
  lib/                 # api.ts · types.ts · colors.ts · useRealtime.ts(WS 自动重连 hook)
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
| GET | `/api/graph/neighbors/{node_id}` | 某节点 1 跳邻居子图（用于「展开邻居」） |
| GET | `/api/search?q=` | 关键词搜索（名称/描述/分类） |
| POST | `/api/rag/query` | RAG 查询（当前为检索层预览，`status=retrieval_ready_no_llm`） |
| GET | `/api/realtime/history` | 最近实时事件（REST 兜底） |
| POST | `/api/ingest/wikipedia` | 触发一轮 Wikipedia 数据接入（body：`{"titles": [...], "max_relations": 20}`） |
| GET | `/api/ingest/runs` | 最近的 ingestion 运行记录 |
| WS | `/api/ws` | 实时事件通道（发送 `ping` 回 `pong` 心跳） |

## 数据模型

`KnowledgeNode`：`id · name · category · description · source · source_url · popularity · created_at · updated_at`

`KnowledgeRelation`：`source_id → target_id`，`relation_type ∈ { subfield_of, is_a, part_of, used_in, based_on, related_to }`

`IngestionRun`：`source · status · fetched · inserted · updated · skipped · relations_created · started_at · finished_at`

分类：`field / paradigm / algorithm / model / architecture / technique / concept / task / dataset / application`

## 开发阶段进度

- [x] **Phase 0** — 项目基础（前后端骨架、数据库、完整数据链路 `Frontend → Backend → DB`）
- [x] **Phase 1** — Seed Data（119 真实节点 / 235 关系，可查询可持久化）
- [x] **Phase 2** — Knowledge Graph（力导向图可视化 · 搜索定位 · 节点详情 · 相关知识 · 图导航：聚焦 / 展开邻居 / 关系筛选 / 重置全图）
- [x] **Phase 3** — Real-time System（WebSocket 事件流 · 实时 Activity Feed · 实时趋势榜 · 图节点实时活动光环 · 自动重连）
- [x] **Phase 4** — Real Data Integration（Wikipedia ingestion pipeline：拉取 → 清洗 → 去重 → 实体链接 → 关系抽取 → 幂等写入 + 运行记录，CLI 与 REST 均可触发）
- [ ] Phase 5 — 语义搜索（Embedding + 向量库）
- [ ] Phase 6 — RAG（接入 LLM，生成 grounded answer）
- [ ] Phase 7 — Agent（Tool Calling / 多步推理）

## 关于实时系统（Phase 3）

`backend/app/services/realtime.py` 在启动时挂起一个后台事件循环，通过 `WS /api/ws` 广播事件：

| 事件类型 | 含义 | 数据是否真实 |
|---|---|---|
| `node_activity` | 随机知识节点活跃度 +Δ（**真实写入 popularity**） | 真实状态变化 |
| `user_activity` | 模拟用户 探索/搜索/打开 某个真实节点 | 模拟系统动态 |
| `trending_update` | 按 popularity 实时重算趋势榜 | 由真实数据计算 |
| `system_status` | 偶发的系统状态播报 | 模拟系统动态 |

> 遵循「Mock Data 只用于动态系统」原则：实时层模拟的是**系统运行状态**（用户活动 / 访问量 / 趋势 / 系统事件），事件指向的都是 seed_data 里的真实知识节点，不伪造知识本身。

前端 `lib/useRealtime.ts` 负责连接、心跳与自动重连（指数退避）；Dashboard 的 Live Activity + Trending、Graph 页的节点「呼吸光环」都由该事件流驱动，全程无需刷新页面。

---

## 关于数据接入（Phase 4）

`backend/app/ingest/` 实现了首个真实数据源的 ingestion pipeline（Wikipedia）：

```text
Wikipedia REST / Action API
        ↓  拉取
数据清洗（合并空白 / 截断 / 规范化 slug）
        ↓
分类映射（Wikipedia 分类 → 项目 taxonomy）
        ↓
去重（slug / 名称对齐已有节点；命中则更新、否则插入）
        ↓
实体链接 + 关系抽取（内部链接对齐已有节点 → related_to）
        ↓
幂等写入 KnowledgeNode / KnowledgeRelation + 记录 IngestionRun
```

两种触发方式：

```bash
# CLI（幂等可重复）
cd backend
.venv\Scripts\python -m app.ingest --titles "Transformer (deep learning)" "BERT (language model)" "Diffusion model"
```

```bash
# REST
curl -X POST http://127.0.0.1:8000/api/ingest/wikipedia \
  -H "Content-Type: application/json" \
  -d '{"titles": ["Transformer (deep learning)", "BERT (language model)"], "max_relations": 20}'
```

特性与验收对照：

- **至少 1 个真实数据源**：Wikipedia（REST summary + Action API，仅标准库 `urllib` + User-Agent）。
- **自动获取数据**：CLI / REST 触发即自动拉取，无需手工整理。
- **基本数据清洗**：合并空白、截断摘要、规范化 slug、剥离消歧义括号。
- **处理重复数据**：slug + 名称去重；重跑同一标题只更新不重复插入；Wikipedia 重定向自动归一到规范条目。
- **统一 Knowledge Node 格式**：外部数据转换为 `KnowledgeNode`/`KnowledgeRelation`。
- **建立/更新关系**：内部链接对齐已有节点生成 `related_to`（重复关系自动跳过）。
- **不破坏已有数据**：更新时仅覆盖 `description / source / source_url`，保留 `id / name / popularity / 已有关系`。
- **记录数据来源**：`source=Wikipedia` + `source_url`；每次运行写入 `ingestion_runs` 表。
- **可重复执行**：幂等（重跑 `inserted=0`，关系收敛后不再重复创建）。

> 已知边界：去重基于 slug/名称的精确对齐，不解决跨别名实体消歧（例如 Wikipedia 的
> `Long short-term memory` 与 seed 里的缩写 `LSTM` 会被视为两个节点）。深度实体解析
> 属于后续阶段的实体链接增强，本阶段用「标题→slug + 名称」的对齐已满足基本去重要求。

---

## 关于 RAG 接口（留接口阶段）

`backend/app/services/rag_service.py` 已定义查询层接口：

```text
User Question → 检索(关键词匹配) → Retrieve Sources → [Phase 6: LLM] → Grounded Answer
```

当前 `retrieve()` 使用关键词加权匹配（临时实现），`query()` 返回检索到的节点与上下文，
`answer` 字段为 `None`。Phase 5 将替换为 embedding + 向量检索，Phase 6 接入 LLM。
