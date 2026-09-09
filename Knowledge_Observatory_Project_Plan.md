# Knowledge Observatory

> 一个以 OC 世界观为视觉与叙事外壳、以真实世界知识为核心数据的未来文明知识观测与交互系统。

---

## 1. 项目定位

本项目不是传统的 OC 展示网站，而是一个具有完整前后端架构的 **Knowledge Observatory（知识观测站）**。

核心思想：

```text
真实世界知识
      ↓
Knowledge Graph
      ↓
知识检索 / 关系分析 / 推荐
      ↓
RAG / AI Agent
      ↓
实时交互与可视化
```

OC 世界观负责：

- UI 视觉风格
- 世界观叙事
- 系统命名
- 用户体验
- 部分虚构的系统状态

而**知识本身尽量使用真实世界数据**，避免为了填充数据库而虚构大量论文、文章和知识。

---

# 2. 核心设计原则

## 2.1 真实知识 + 虚构系统

不建立一个完全虚构的“未来知识库”。

而是：

> **现实世界知识作为底层数据，OC 世界观作为观察这些知识的方式。**

例如数据库中的知识可以是真实的：

```text
Artificial Intelligence
 ├── Machine Learning
 ├── Deep Learning
 ├── Computer Vision
 └── Reinforcement Learning
```

而前端将其呈现为未来文明中的：

> Civilization Knowledge Network

---

## 2.2 Seed Data 作为系统初始状态

项目初期不需要接入庞大的外部数据源。

首先建立一批规模较小的真实知识数据作为：

> **Seed Data**

例如：

```text
100–500 个真实 Knowledge Nodes
```

通过 Seed Data：

- 验证数据库设计
- 验证 Graph 数据结构
- 开发前端可视化
- 开发搜索
- 开发关系查询
- 开发推荐
- 开发实时更新

后续再逐渐扩大数据规模。

---

## 2.3 Mock Data 只用于动态系统

不建议用大量 Mock Data 假装成真实知识。

可以模拟的是：

- 用户活动
- 知识访问量
- Trending Score
- Knowledge Activity
- 新知识事件
- 系统状态
- 实时事件

例如：

```text
Knowledge Activity

Transformer       ██████████████████
Computer Vision   █████████████
CNN               █████████
RNN               █████
```

这些属于系统运行状态，可以使用模拟数据。

---

# 3. 核心功能

## 3.1 Knowledge Graph

项目最核心的功能。

用户可以通过图结构探索知识：

```text
Machine Learning
       │
 ┌─────┼─────┐
 ↓     ↓     ↓
CNN   RNN   RL
 │
 ↓
ResNet
```

Knowledge Node 至少包含：

```text
id
name
category
description
source
source_url
related_nodes
```

后续可以增加：

```text
embedding
popularity
activity
created_at
updated_at
```

---

# 4. 知识数据来源

优先使用真实、公开的数据来源。

候选来源：

- Wikipedia
- Wikidata
- arXiv
- OpenAlex
- Crossref
- PubMed
- GitHub 等公开数据源

项目初期不要求全部接入。

推荐路线：

```text
Phase 1
Seed Data
   ↓
Phase 2
单一真实数据源
   ↓
Phase 3
多个数据源
```

---

# 5. 实时系统

“实时”不是为了强行使用 WebSocket，而是让实时通信服务于系统状态变化。

重点展示：

### 实时知识活动

例如：

```text
NEW KNOWLEDGE ACTIVITY

Vision Transformer
↓
Computer Vision
↓
Attention
```

前端 Graph 实时出现新的关系或节点状态。

---

### 实时用户活动

例如：

```text
USER ACTIVITY

User #1024
explored → ResNet

User #2811
searched → Transformer

User #0192
opened → Reinforcement Learning
```

这些数据可以使用 Mock Data。

---

### 实时任务状态

例如用户发起：

```text
Analyze Knowledge Graph
```

后端：

```text
Queued
   ↓
Processing
   ↓
Graph Analysis
   ↓
Completed
```

前端实时更新状态。

---

# 6. 搜索与知识探索

用户可以：

```text
Search
  ↓
Find Knowledge Nodes
  ↓
Open Node
  ↓
Explore Relations
  ↓
Recommended Knowledge
```

例如搜索：

> ResNet

显示：

```text
ResNet

Related Concepts:
- CNN
- Deep Learning
- Image Classification
- Residual Learning

Related Research:
- ...
```

---

# 7. Knowledge Recommendation

用户查看一个 Knowledge Node 后，系统根据：

- Graph relationship
- Semantic similarity
- Category
- User activity

推荐相关知识。

例如：

```text
You may also explore:

1. DenseNet
2. EfficientNet
3. Vision Transformer
4. Feature Pyramid Network
```

后续可以加入：

- Embedding
- Vector Search
- Recommendation Model

---

# 8. RAG

RAG 不作为独立的“聊天机器人”存在，而是作为 Knowledge Observatory 的查询层。

用户提出：

> ResNet 和 Transformer 在计算机视觉中的关系是什么？

系统流程：

```text
User Question
      ↓
Question Understanding
      ↓
Knowledge Graph Search
      ↓
Vector Search
      ↓
Retrieve Sources
      ↓
LLM
      ↓
Grounded Answer
```

回答同时引用相关 Knowledge Nodes。

---

# 9. AI Agent

后续加入 Agent，而不是项目初期就加入。

Agent 可以负责：

- 分析用户问题
- 决定搜索方式
- 调用 Knowledge Graph
- 调用 Vector Search
- 检索真实资料
- 整理结果
- 生成回答

整体：

```text
                 User
                   ↓
              AI Agent
             ↙    ↓    ↘
       Graph Search  Vector Search
             ↘    ↓    ↙
            Knowledge Base
                   ↓
                  LLM
                   ↓
                Answer
```

---

# 10. 前端设计

前端核心不是普通网页，而是一个：

> **未来文明知识观测系统**

主要界面：

### Dashboard

显示：

```text
Knowledge Nodes
Connections
Active Research
Trending Topics
System Activity
```

---

### Knowledge Graph

核心交互界面：

- 节点
- 边
- 分类
- 搜索
- 聚焦
- 展开
- 节点详情
- 动态更新

---

### Knowledge Detail

点击节点后显示：

```text
Knowledge

Description

Related Concepts

Research

Sources

Activity

Recommended Knowledge
```

---

### AI Explorer

用于：

- 自然语言查询
- RAG
- Agent
- 知识探索

---

# 11. 后端设计

后端至少承担：

```text
Frontend
    ↓
API
    ↓
Backend
    ├── Knowledge Service
    ├── Search Service
    ├── Graph Service
    ├── Recommendation Service
    ├── RAG Service
    └── Realtime Service
```

后续可以进一步拆分。

---

# 12. 数据库设计

初期可以保持简单。

核心实体：

```text
KnowledgeNode
KnowledgeRelation
Source
User
Activity
```

概念结构：

```text
KnowledgeNode
      │
      ├── KnowledgeRelation
      │
      ├── Source
      │
      └── Activity
```

根据实际技术选型决定最终使用：

- PostgreSQL
- Graph Database
- Vector Database

不要求一开始全部使用。

---

# 13. 推荐技术架构

可以采用：

```text
                 Frontend
                    │
          React / Next.js
                    │
              REST / WebSocket
                    │
                 Backend
                    │
             ┌──────┼──────┐
             ↓      ↓      ↓
         Database  Search  RAG
             │      │      │
             └──────┼──────┘
                    ↓
                  Agent
```

具体技术栈在正式开发前再根据需求确定，不提前为了“技术丰富”而堆技术。

---

# 14. 数据流

完整数据流目标：

```text
Real World Sources
        ↓
Data Collection
        ↓
Data Processing
        ↓
Knowledge Nodes
        ↓
Knowledge Graph
        ↓
Database
        ↓
Backend API
        ↓
Frontend
```

AI 查询：

```text
User
 ↓
Agent
 ↓
Graph Search + Vector Search
 ↓
Retrieve Real Sources
 ↓
LLM
 ↓
Answer
```

实时系统：

```text
Backend Event
 ↓
WebSocket / SSE
 ↓
Frontend
 ↓
UI State Update
```

---

# 15. 开发阶段

## Phase 0 — 项目基础

- [ ] 确定最终技术栈
- [ ] 创建 GitHub Repository
- [ ] 创建 Frontend
- [ ] 创建 Backend
- [ ] 建立基础项目结构
- [ ] 确定 UI 视觉规范
- [ ] 确定 Knowledge Node 数据结构

### 验收标准

- [ ] Frontend 可以独立启动并正常访问
- [ ] Backend 可以独立启动并提供至少一个测试 API
- [ ] Frontend 能成功请求 Backend
- [ ] 数据库能够正常连接
- [ ] 已确定 `KnowledgeNode`、`KnowledgeRelation`、`Source` 等核心数据结构
- [ ] 已确定 Seed Data 的来源与基本数据格式
- [ ] Git Repository、开发环境和基础项目结构可正常使用

**阶段通过条件：**

> 能够从零启动项目，并完成一次 `Frontend → Backend → Database → Backend → Frontend` 的完整数据链路。

---

## Phase 1 — Seed Data

目标：

> 让最小规模的真实知识网络运行起来。

- [ ] 收集第一批真实知识
- [ ] 建立 Seed Data
- [ ] 建立数据库
- [ ] 实现 Knowledge Node
- [ ] 实现 Knowledge Relation
- [ ] 实现基础 API

目标规模：

```text
100–500 Knowledge Nodes
```

### 验收标准

- [ ] 至少导入 **100 个真实 Knowledge Nodes**
- [ ] 至少建立 **200 条 Knowledge Relations**
- [ ] 每个 Knowledge Node 有唯一 ID
- [ ] 核心节点包含名称、分类、描述、来源等基本信息
- [ ] 数据能够持久化到数据库
- [ ] Backend 能够查询 Knowledge Nodes
- [ ] Backend 能够查询 Knowledge Relations
- [ ] 能够根据 Node ID 获取完整节点信息

**阶段通过条件：**

> 数据库中存在一个结构完整、可查询、可持久化的真实知识网络，而不是写死在前端的 JSON。

---

## Phase 2 — Knowledge Graph

- [ ] Graph Visualization
- [ ] Node Interaction
- [ ] Relation Visualization
- [ ] Node Search
- [ ] Node Detail
- [ ] Related Knowledge
- [ ] Graph Traversal

完成后：

> 用户可以真正“探索知识网络”。

### 验收标准

- [ ] Frontend 能够从 Backend 获取知识节点和关系
- [ ] Graph 能够正确显示 Node 和 Edge
- [ ] 点击 Node 可以查看详情
- [ ] 可以搜索 Knowledge Node
- [ ] 搜索结果可以定位到 Graph 中对应节点
- [ ] 可以展开节点的相关知识
- [ ] Graph 数据变化后不需要修改前端代码即可反映新的数据
- [ ] 至少支持一种 Graph Navigation，例如：
  - 展开邻居节点
  - 聚焦节点
  - 隐藏 / 显示关系

**阶段通过条件：**

> 用户可以从一个知识节点出发，通过点击、搜索和关系展开，在整个 Knowledge Graph 中进行探索。

---

## Phase 3 — Real-time System

- [ ] 建立 WebSocket / SSE
- [ ] 实现 Activity Event
- [ ] 实现实时状态更新
- [ ] 实现模拟用户活动
- [ ] 实现新节点 / 新关系事件
- [ ] 前端实时更新 Graph / Dashboard

重点验证：

> **Backend State → Event → Frontend State Update**

### 验收标准

- [ ] 建立 WebSocket 或 SSE 通信
- [ ] Backend 可以产生事件
- [ ] Frontend 可以接收事件
- [ ] 不刷新页面即可更新 UI
- [ ] 至少实现一种真实的实时状态变化
- [ ] Activity Feed 可以实时更新
- [ ] Graph 或 Dashboard 至少有一个组件可以实时变化
- [ ] 能够模拟多个用户 / 系统事件
- [ ] 页面断开连接后能够正确处理重新连接

**阶段通过条件：**

> 在浏览器不刷新页面的情况下，Backend 产生的数据变化能够被 Frontend 接收并反映出来。

---

## Phase 4 — Real Data Integration

逐渐接入真实数据源：

```text
Seed Data
   ↓
Wikipedia / Wikidata
   ↓
Research Data
   ↓
Larger Knowledge Base
```

实现：

- [ ] Data ingestion
- [ ] Data cleaning
- [ ] Deduplication
- [ ] Entity linking
- [ ] Relation extraction
- [ ] 定期更新

### 验收标准

- [ ] 至少接入 **1 个真实数据源**
- [ ] 能够自动获取数据
- [ ] 能够完成基本的数据清洗
- [ ] 能够处理重复数据
- [ ] 能够将外部数据转换成统一的 Knowledge Node 格式
- [ ] 能够建立 / 更新 Knowledge Relations
- [ ] 数据更新不会破坏已有数据
- [ ] 能够记录数据来源
- [ ] 能够重复执行 ingestion pipeline

**阶段通过条件：**

> 删除 / 清空部分 Seed Data 后，可以通过数据 pipeline 从真实数据源重新构建知识数据。

---

## Phase 5 — Semantic Search

加入：

- [ ] Embedding
- [ ] Vector Database
- [ ] Semantic Search
- [ ] Similarity Search
- [ ] Knowledge Recommendation

实现：

```text
Keyword Search
+
Semantic Search
+
Graph Search
```

### 验收标准

- [ ] Knowledge Nodes 可以生成 Embedding
- [ ] Embedding 可以持久化
- [ ] 建立 Vector Search
- [ ] 用户输入自然语言查询
- [ ] 系统能够返回语义相关节点
- [ ] 搜索结果不仅依赖关键词完全匹配
- [ ] 能够比较 Keyword Search 与 Semantic Search 的结果
- [ ] Knowledge Recommendation 可以使用语义相似度

**阶段通过条件：**

> 对一个不包含目标知识名称的自然语言查询，系统仍然能够找到语义相关的 Knowledge Nodes。

---

## Phase 6 — RAG

- [ ] Document retrieval
- [ ] Context construction
- [ ] Source citation
- [ ] RAG pipeline
- [ ] Knowledge-grounded QA

目标：

> AI 的回答必须尽可能建立在实际检索到的知识上，而不是单纯依赖 LLM 记忆。

### 验收标准

- [ ] 可以从真实数据源获取文档 / 内容
- [ ] 文档可以被切分
- [ ] 文档可以建立 Embedding
- [ ] 用户可以提出自然语言问题
- [ ] 系统能够执行 Retrieval
- [ ] LLM 使用 Retrieval Context 生成回答
- [ ] 回答能够提供来源
- [ ] 无相关资料时能够明确说明，而不是强行生成答案
- [ ] 能够查看回答使用了哪些资料

**阶段通过条件：**

> 对一个具体问题，可以追溯 AI 回答所依据的真实资料。

---

## Phase 7 — Agent

最后加入：

- [ ] Agent
- [ ] Tool Calling
- [ ] Graph Search Tool
- [ ] Vector Search Tool
- [ ] Source Retrieval Tool
- [ ] RAG Tool
- [ ] Multi-step reasoning workflow

目标：

```text
Question
 ↓
Agent
 ↓
Decide what to retrieve
 ↓
Call Tools
 ↓
Analyze results
 ↓
Generate grounded answer
```

### 验收标准

- [ ] Agent 能够理解用户任务
- [ ] 至少提供 3 个 Tools
- [ ] Agent 能够根据问题选择 Tool
- [ ] 至少支持多步骤 Tool Calling
- [ ] 可以调用 Knowledge Graph
- [ ] 可以调用 Semantic Search / Vector Search
- [ ] 可以调用 Source Retrieval
- [ ] Agent 能够整合多个 Tool 的结果
- [ ] 最终回答能够提供依据
- [ ] 能够记录 Agent 执行过程

**阶段通过条件：**

> 面对不同类型的问题，Agent 不再固定执行同一条流程，而是能够选择不同工具并完成多步骤知识探索。

---

# 16. Mock Data 策略

Mock Data 主要用于展示系统动态能力。

可以模拟：

```text
User Activity
Knowledge Activity
Search Activity
System Events
Trending Score
Realtime Updates
```

例如后端每隔一定时间产生：

```text
EVENT

User explored:
"Computer Vision"

Activity +1
```

或者：

```text
EVENT

Knowledge Activity detected:

Transformer
```

前端收到事件后更新：

```text
Dashboard
Graph
Activity Feed
Trending
```

这样可以在没有大量真实用户的情况下展示实时系统。

---

# 17. 项目的核心技术亮点

项目最终希望能够体现：

### Frontend

- Interactive Knowledge Graph
- Complex UI State
- Data Visualization
- Real-time UI Updates
- Search & Exploration
- AI Interaction

### Backend

- REST API
- Database
- Knowledge Graph
- Data Pipeline
- Search
- Recommendation
- RAG
- Agent
- Real-time Event System

### AI

- Embeddings
- Vector Search
- RAG
- Tool Calling
- Agentic Workflow

---

# 18. 项目不做什么

为了控制项目规模，明确以下边界：

- 不人为编写大量虚构论文
- 不人为创造大量虚构知识
- 不为了展示技术而堆叠数据库
- 不一开始接入大量数据源
- 不一开始实现复杂 Agent
- 不把项目做成单纯的 AI Chatbot
- 不把项目做成单纯的 OC Wiki
- 不把实时通信变成没有实际意义的“假实时”

---

# 19. 最终目标

最终系统形成：

```text
                 KNOWLEDGE OBSERVATORY
                          │
          ┌───────────────┼───────────────┐
          ↓               ↓               ↓
       Knowledge       Knowledge       Research
         Graph           Search          Data
          │               │               │
          └───────────────┼───────────────┘
                          ↓
                     RAG / Agent
                          │
                          ↓
                   AI Knowledge
                     Explorer
                          │
                          ↓
                 Real-time System
```

其中：

> **真实世界知识是数据基础。**

> **Knowledge Graph 是核心结构。**

> **RAG / Agent 是智能交互层。**

> **WebSocket / SSE 是实时响应层。**

> **OC 世界观是整个系统的视觉与叙事框架。**

---

# 20. 项目最终形态

用户打开网站后，不是看到一个普通的个人作品集，而是进入一个虚构的未来文明系统：

```text
┌──────────────────────────────────────┐
│      CIVILIZATION KNOWLEDGE          │
│             OBSERVATORY              │
├──────────────────────────────────────┤
│                                      │
│  Knowledge Nodes       284,193       │
│  Connections           812,391       │
│  Active Research       12,381       │
│  System Activity       LIVE          │
│                                      │
│         [ KNOWLEDGE GRAPH ]          │
│                                      │
│             ●────●                   │
│           ╱ │    │ ╲                 │
│          ●  ●────●  ●                │
│             │                         │
│             ●                         │
│                                      │
├──────────────────────────────────────┤
│ LIVE ACTIVITY                        │
│                                      │
│ New connection detected...           │
│ User exploring Computer Vision...    │
│ Knowledge activity updated...        │
└──────────────────────────────────────┘
```

而用户可以从：

**观察 → 搜索 → 探索 → 发现关系 → 阅读真实资料 → 向 AI 提问 → 获取检索增强的回答**

完成整个知识探索流程。

最终项目不是“一个 OC 网站”，而是：

> **一个以真实世界知识为基础、以未来文明为叙事框架的实时 Knowledge Observatory。**
