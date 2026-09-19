# 测试报告 · Testing

> Knowledge Observatory 后端自动化测试报告。测试框架：Python 标准库 `unittest`（零新增依赖）。

## 一、运行方式

```bash
cd backend
.venv\Scripts\python -m unittest discover -s tests -t . -v   # Windows
# macOS / Linux
python -m unittest discover -s tests -t . -v
```

- 每个测试方法使用**独立的临时 SQLite 数据库**（位于 `backend/.tests_tmp/`，已被 `.gitignore` 忽略），保证隔离与可重复。
- 测试全程**不访问网络**：LLM 调用用本地 mock HTTP 服务验证，Wikipedia 只测纯函数（slugify / 清洗 / 分类映射）。
- 测试会强制走「无 LLM」路径（mock 掉 `LLM_API_BASE`），不依赖本机 `.env`，结果确定。

## 二、测试结果（最近一次实际运行）

| 指标 | 值 |
|---|---|
| 结果 | ✅ **OK** |
| 用例总数 | **43** |
| 通过 | **43** |
| 失败 / 错误 | **0** |
| 耗时 | **约 4.0 s**（43 tests） |

```
Ran 43 tests in 3.980s

OK
```

## 三、测试清单与结果

### `tests/test_seed.py` — 3 个用例（Phase 1 Seed Data）
| 用例 | 结果 |
|---|---|
| test_seed_counts | ✅ |
| test_seed_idempotent | ✅ |
| test_node_fields_present | ✅ |

### `tests/test_ingest.py` — 9 个用例（Phase 4 数据接入，纯函数）
| 用例 | 结果 |
|---|---|
| test_slugify_strips_disambiguation | ✅ |
| test_slugify_spaces | ✅ |
| test_slugify_underscores_and_case | ✅ |
| test_clean_extract_collapses_whitespace | ✅ |
| test_clean_extract_truncates | ✅ |
| test_map_architecture | ✅ |
| test_map_field | ✅ |
| test_map_dataset | ✅ |
| test_map_default_concept | ✅ |

### `tests/test_semantic.py` — 5 个用例（Phase 5 语义搜索）
| 用例 | 结果 |
|---|---|
| test_embeddings_built_for_all_nodes | ✅ |
| test_semantic_search_finds_concept_without_exact_name | ✅ |
| test_semantic_search_translation | ✅ |
| test_recommend_excludes_self | ✅ |
| test_ensure_embeddings_no_rebuild_when_fresh | ✅ |

### `tests/test_rag.py` — 4 个用例（Phase 6 RAG）
| 用例 | 结果 |
|---|---|
| test_query_no_llm_returns_retrieval | ✅ |
| test_query_retrieves_relevant_nodes | ✅ |
| test_query_no_context | ✅ |
| test_retrieve_returns_tuples_with_score | ✅ |

### `tests/test_llm.py` — 4 个用例（Phase 6/7 LLM 客户端，本地 mock）
| 用例 | 结果 |
|---|---|
| test_configured | ✅ |
| test_chat_parses_content | ✅ |
| test_chat_raises_when_unconfigured | ✅ |
| test_chat_raises_on_http_error | ✅ |

### `tests/test_agent.py` — 7 个用例（Phase 7 Agent）
| 用例 | 结果 |
|---|---|
| test_four_tools_registered | ✅ |
| test_call_each_tool | ✅ |
| test_relation_intent_uses_graph_search | ✅ |
| test_run_persists_agent_run | ✅ |
| test_parse_action | ✅ |
| test_parse_action_final | ✅ |
| test_parse_invalid_returns_none | ✅ |

### `tests/test_routers.py` — 11 个用例（API 路由层，直调端点函数）
| 用例 | 结果 |
|---|---|
| test_health / test_stats | ✅ |
| test_get_node / test_get_node_not_found | ✅ |
| test_full_graph / test_neighbors | ✅ |
| test_search_hits | ✅ |
| test_compare | ✅ |
| test_rag_query | ✅ |
| test_agent_query / test_agent_runs | ✅ |

## 四、覆盖范围（按 Phase）

| Phase | 覆盖内容 | 状态 |
|---|---|---|
| Phase 1 Seed Data | 节点/关系数量、字段完整性、seed 幂等 | ✅ |
| Phase 4 数据接入 | slugify、清洗、分类映射（纯函数） | ✅ |
| Phase 5 语义搜索 | 向量持久化、语义检索、推荐、索引判重 | ✅ |
| Phase 6 RAG | 混合检索、no_llm / no_context 分支 | ✅ |
| Phase 6/7 LLM | 客户端配置、响应解析、错误处理（mock） | ✅ |
| Phase 7 Agent | 4 工具、意图选工具、多步、轨迹持久化、JSON 解析 | ✅ |
| 路由层 | health/stats/nodes/graph/search/semantic/rag/agent | ✅ |

## 五、说明与已知限制

- **LLM 与网络**：测试不发起真实网络请求；`LLMClient` 用本地 `http.server` mock 验证，保证离线可跑、可重复。
- **WebSocket（Phase 3 实时系统）**：实时事件循环依赖 `asyncio` 后台任务，未纳入单测；其逻辑已通过手动端到端验证（`/api/ws` + 事件流）。
- **Wikipedia 拉取（Phase 4 网络部分）**：仅测纯函数；真实抓取需网络，已通过手动 `python -m app.ingest` 验证。
- **弃用警告**：运行时会看到一条 `datetime.datetime.utcnow()` 的 `DeprecationWarning`（来自 SQLAlchemy 模型默认值），不影响测试结果。
- **沙箱说明**：`backend/.tests_tmp/` 目录不使用 `tempfile.mkdtemp()`（DSH 沙箱下其创建的目录对 SQLite 不可见），改用 `uuid` 手工建目录。
