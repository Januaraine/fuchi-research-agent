"""AI Agent（Phase 7）。

一个可多步调用工具的「知识探索 Agent」：
- 4 个工具：vector_search（向量检索）/ graph_search（图遍历）/ source_retrieve（来源检索）/ rag_answer（RAG）
- LLM 已配置时走 ReAct 循环：每步让 LLM 选择「调用哪个工具」或「给出最终答案」，可多步；
- LLM 未配置时走确定性 fallback：按问题意图选择工具、多步探索并汇总（保证无 key 也可演示）；
- 全程记录执行轨迹（steps）与依据（evidence），并持久化到 agent_runs 表。
"""
from __future__ import annotations

import json
import re

from sqlalchemy.orm import Session

from .. import models
from . import embedding_service
from .llm import LLMClient, LLMError
from .rag_service import RAGService

TOOL_DEFS: list[dict] = [
    {
        "name": "vector_search",
        "description": "按自然语言语义检索相关知识节点（向量相似度）。",
        "params": {"query": "string", "k": "int=5"},
    },
    {
        "name": "graph_search",
        "description": "探索某节点在图中的邻居与关系（图遍历）。",
        "params": {"node_id": "string", "depth": "int=1"},
    },
    {
        "name": "source_retrieve",
        "description": "获取某节点的完整信息与真实来源（描述 + source_url）。",
        "params": {"node_id": "string"},
    },
    {
        "name": "rag_answer",
        "description": "对问题做检索增强问答（RAG），生成带引用的 grounded answer。",
        "params": {"question": "string"},
    },
]

AGENT_SYSTEM = """You are the Knowledge Observatory agent. You explore a knowledge base of real-world AI/ML concepts by calling tools, possibly over multiple steps.

Available tools:
{tools}

For each step respond with ONLY one JSON object (no prose, no markdown fence):
{{"action": "<tool_name>", "args": {{<params>}}}}

To finish, respond with ONLY:
{{"action": "final", "answer": "<your grounded answer, cite sources as [n]>", "evidence": ["<node_id>", ...]}}

Decide the next action from the question and previous observations. Prefer vector_search first, then graph_search / source_retrieve to gather evidence, then final. You may call tools multiple times."""


class AgentService:
    def __init__(self, db: Session):
        self.db = db
        self.rag = RAGService(db)
        self.llm = LLMClient()
        self.seen_node_ids: set[str] = set()

    # ---- tools ----
    def _vector_search(self, query: str, k: int = 5) -> dict:
        hits = embedding_service.semantic_search(self.db, query, k)
        self.seen_node_ids.update(h["id"] for h in hits)
        return {"hits": hits}

    def _graph_search(self, node_id: str, depth: int = 1) -> dict:
        node = self.db.get(models.KnowledgeNode, node_id)
        if node is None:
            return {"error": f"node not found: {node_id}"}
        self.seen_node_ids.add(node_id)

        visited: set[str] = {node_id}
        frontier = {node_id}
        for _ in range(max(1, depth)):
            neighbors: set[str] = set()
            for nid in frontier:
                out = {r.target_id for r in self.db.query(models.KnowledgeRelation).filter_by(source_id=nid)}
                inc = {r.source_id for r in self.db.query(models.KnowledgeRelation).filter_by(target_id=nid)}
                neighbors |= out | inc
            frontier = neighbors - visited
            visited |= frontier

        self.seen_node_ids.update(visited)
        rels = (
            self.db.query(models.KnowledgeRelation)
            .filter(
                models.KnowledgeRelation.source_id.in_(visited),
                models.KnowledgeRelation.target_id.in_(visited),
            )
            .all()
        )
        names = {n.id: n.name for n in self.db.query(models.KnowledgeNode).filter(models.KnowledgeNode.id.in_(visited))}
        return {
            "center": node_id,
            "nodes": [{"id": i, "name": names.get(i, i)} for i in sorted(visited)],
            "relations": [
                {"source": r.source_id, "target": r.target_id, "type": r.relation_type}
                for r in rels
            ],
        }

    def _source_retrieve(self, node_id: str) -> dict:
        node = self.db.get(models.KnowledgeNode, node_id)
        if node is None:
            return {"error": f"node not found: {node_id}"}
        self.seen_node_ids.add(node_id)
        return {
            "id": node.id,
            "name": node.name,
            "category": node.category,
            "description": node.description,
            "source": node.source,
            "source_url": node.source_url,
        }

    def _rag_answer(self, question: str) -> dict:
        result = self.rag.query(question)
        self.seen_node_ids.update(s["id"] for s in result.get("retrieved", []))
        return {
            "status": result["status"],
            "answer": result.get("answer"),
            "retrieved": result.get("retrieved", []),
        }

    def _call_tool(self, name: str, args: dict) -> dict:
        if name == "vector_search":
            return self._vector_search(str(args.get("query", "")), int(args.get("k", 5)))
        if name == "graph_search":
            return self._graph_search(str(args.get("node_id", "")), int(args.get("depth", 1)))
        if name == "source_retrieve":
            return self._source_retrieve(str(args.get("node_id", "")))
        if name == "rag_answer":
            return self._rag_answer(str(args.get("question", "")))
        return {"error": f"unknown tool: {name}"}

    # ---- helpers ----
    @staticmethod
    def _summarize(obs: dict, max_len: int = 400) -> str:
        text = json.dumps(obs, ensure_ascii=False)
        return text if len(text) <= max_len else text[:max_len] + "…"

    def _evidence(self) -> list[dict]:
        ev: list[dict] = []
        for nid in self.seen_node_ids:
            node = self.db.get(models.KnowledgeNode, nid)
            if node is not None:
                ev.append(
                    {"id": node.id, "name": node.name, "category": node.category, "source_url": node.source_url}
                )
        return ev

    def _record(self, question: str, status: str, llm_used: bool, answer: str, steps: list[dict], evidence: list[dict]) -> int:
        run = models.AgentRun(
            question=question,
            status=status,
            llm_used=llm_used,
            answer=answer,
            steps_json=json.dumps(steps, ensure_ascii=False),
            evidence_json=json.dumps(evidence, ensure_ascii=False),
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run.id

    # ---- agent loops ----
    def run(self, question: str, max_steps: int = 6) -> dict:
        if self.llm.configured:
            return self._run_llm(question, max_steps)
        return self._run_fallback(question)

    def _run_llm(self, question: str, max_steps: int) -> dict:
        tool_schema = "\n".join(
            f"- {t['name']}({', '.join(f'{k}: {v}' for k, v in t['params'].items())}): {t['description']}"
            for t in TOOL_DEFS
        )
        system = AGENT_SYSTEM.format(tools=tool_schema)
        history: list[str] = []
        steps: list[dict] = []

        for i in range(max(1, max_steps)):
            user = (
                f"Question: {question}\n\n"
                f"Previous observations:\n" + ("\n".join(history) if history else "(none)") +
                f"\n\nStep {i + 1}: output ONE JSON object."
            )
            try:
                raw = self.llm.chat(system, user)
            except LLMError as exc:
                return self._finish(question, "error", True, f"LLM 调用失败：{exc}", steps)

            parsed = self._parse_action(raw)
            if parsed is None or parsed.get("action") == "final":
                answer = (parsed or {}).get("answer", raw) if parsed else raw
                for eid in (parsed or {}).get("evidence", []) or []:
                    self.seen_node_ids.add(str(eid))
                return self._finish(question, "completed", True, answer, steps)

            name = str(parsed.get("action", ""))
            args = parsed.get("args") or {}
            if not isinstance(args, dict):
                args = {}
            if name not in {t["name"] for t in TOOL_DEFS}:
                history.append(f"step {i + 1}: unknown tool '{name}'")
                continue

            obs = self._call_tool(name, args)
            summary = self._summarize(obs)
            steps.append({"step": i + 1, "action": name, "args": args, "observation": summary})
            history.append(f"step {i + 1}: {name}({json.dumps(args, ensure_ascii=False)}) -> {summary}")

        return self._finish(question, "completed", True, self._fallback_answer(question), steps)

    def _run_fallback(self, question: str) -> dict:
        """无 LLM 时的确定性多步探索（按意图选工具）。"""
        steps: list[dict] = []
        ql = question.lower()

        vec = self._vector_search(question, 5)
        steps.append({"step": 1, "action": "vector_search", "args": {"query": question, "k": 5}, "observation": self._summarize(vec)})
        top = vec["hits"][0]["id"] if vec.get("hits") else None

        if top and any(k in question + " " + ql for k in ["关系", "相关", "连接", "related", "relation", "neighbor", "子领域", "connection"]):
            g = self._graph_search(top, 1)
            steps.append({"step": 2, "action": "graph_search", "args": {"node_id": top, "depth": 1}, "observation": self._summarize(g)})
        elif top and any(k in question + " " + ql for k in ["来源", "资料", "依据", "source", "reference", "cite"]):
            s = self._source_retrieve(top)
            steps.append({"step": 2, "action": "source_retrieve", "args": {"node_id": top}, "observation": self._summarize(s)})

        rag = self._rag_answer(question)
        steps.append({"step": len(steps) + 1, "action": "rag_answer", "args": {"question": question}, "observation": self._summarize({"status": rag["status"], "retrieved": [x["name"] for x in rag["retrieved"]]})})

        answer = self._fallback_answer(question)
        return self._finish(question, "no_llm", False, answer, steps)

    def _fallback_answer(self, question: str) -> str:
        if not self.seen_node_ids:
            return "未在知识库中找到相关资料。"
        ev = self._evidence()
        head = "\n".join(f"[{i + 1}] {e['name']}（{e['category']}）" for i, e in enumerate(ev[:5]))
        return f"基于多步工具探索（向量检索 → 图遍历 / 来源检索 → RAG），找到以下相关知识点：\n{head}\n\n（未配置 LLM，以上为确定性汇总；配置 LLM 后由 Agent 生成带引用的完整回答。）"

    def _finish(self, question: str, status: str, llm_used: bool, answer: str, steps: list[dict]) -> dict:
        evidence = self._evidence()
        run_id = self._record(question, status, llm_used, answer, steps, evidence)
        return {
            "run_id": run_id,
            "question": question,
            "status": status,
            "llm_used": llm_used,
            "answer": answer,
            "steps": steps,
            "evidence": evidence,
        }

    @staticmethod
    def _parse_action(raw: str) -> dict | None:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None

    @staticmethod
    def tool_infos() -> list[dict]:
        return TOOL_DEFS
