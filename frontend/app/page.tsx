"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useRealtime } from "@/lib/useRealtime";
import { CATEGORY_COLORS, CATEGORY_LABELS, FALLBACK_COLOR } from "@/lib/colors";
import NodeCard from "@/components/NodeCard";
import StatCard from "@/components/StatCard";
import ActivityFeed from "@/components/ActivityFeed";
import TrendingPanel from "@/components/TrendingPanel";
import SemanticSearch from "@/components/SemanticSearch";
import AgentExplorer from "@/components/AgentExplorer";
import type { NodeSummary, RagResult, Stats } from "@/lib/types";

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [fields, setFields] = useState<NodeSummary[]>([]);
  const [error, setError] = useState<string | null>(null);

  const [question, setQuestion] = useState("");
  const [rag, setRag] = useState<RagResult | null>(null);
  const [ragBusy, setRagBusy] = useState(false);

  const { connected, events, trending } = useRealtime(40);

  useEffect(() => {
    Promise.all([api.stats(), api.nodes({ category: "field" })])
      .then(([s, f]) => {
        setStats(s);
        setFields(f);
      })
      .catch((e) => setError(String(e)));
  }, []);

  const ask = async () => {
    const q = question.trim();
    if (!q) return;
    setRagBusy(true);
    setRag(null);
    try {
      setRag(await api.ragQuery(q));
    } catch (e) {
      setRag({
        question: q,
        status: "error",
        message: String(e),
        answer: null,
        retrieved: [],
        context: null,
      });
    } finally {
      setRagBusy(false);
    }
  };

  if (error)
    return (
      <div className="shell state">
        无法连接后端 API：{error}（请确认 backend 已在 8000 端口运行）
      </div>
    );

  return (
    <div className="shell">
      <section className="hero">
        <div className="kicker">Civilization Knowledge Network</div>
        <h1>
          未来文明<span className="accent">知识观测站</span>
          <br />
          Knowledge Observatory
        </h1>
        <p>
          以真实世界知识为底层数据、以未来文明为叙事框架。观察 → 搜索 → 探索 → 发现关系 →
          阅读真实资料 → 向 AI 提问。
        </p>
        <div style={{ marginTop: 24 }}>
          <Link href="/graph" className="btn">
            进入知识图谱 →
          </Link>
        </div>
      </section>

      {stats && (
        <div className="stats-grid">
          <StatCard label="Knowledge Nodes" value={stats.nodes.toLocaleString()} />
          <StatCard label="Connections" value={stats.relations.toLocaleString()} />
          <StatCard
            label="Categories"
            value={Object.keys(stats.categories).length}
          />
        </div>
      )}

      <section className="section">
        <h2>
          <span className="id">01</span>实时观测{" "}
          <span className={`live-badge ${connected ? "on" : "off"}`} style={{ marginLeft: 8 }}>
            <span className="live-dot" />
            {connected ? "LIVE" : "RECONNECTING"}
          </span>
        </h2>
        <div className="live-grid">
          <div className="panel">
            <h3>Live Activity</h3>
            <ActivityFeed events={events} empty="正在连接实时事件流…" />
          </div>
          <div className="panel">
            <h3>Trending Knowledge</h3>
            <TrendingPanel items={trending} />
          </div>
        </div>
      </section>

      <section className="section">
        <h2>
          <span className="id">02</span>知识分类
        </h2>
        <div className="chips">
          {stats &&
            Object.entries(stats.categories).map(([cat, count]) => (
              <span className="chip" key={cat}>
                <span
                  className="dot"
                  style={{ background: CATEGORY_COLORS[cat] ?? FALLBACK_COLOR }}
                />
                {CATEGORY_LABELS[cat] ?? cat} <span className="count">{count}</span>
              </span>
            ))}
        </div>
      </section>

      <section className="section">
        <h2>
          <span className="id">03</span>核心领域
        </h2>
        <div className="node-grid">
          {fields.map((n) => (
            <NodeCard key={n.id} node={n} />
          ))}
        </div>
      </section>

      <section className="section">
        <h2>
          <span className="id">04</span>AI Explorer{" "}
          <span className="muted" style={{ fontSize: 12, fontFamily: "var(--mono)" }}>
            （RAG · 检索增强）
          </span>
        </h2>
        <div className="panel explorer-box">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="例如：ResNet 和 Transformer 在计算机视觉中的关系是什么？"
          />
          <div style={{ marginTop: 10 }}>
            <button className="btn" onClick={ask} disabled={ragBusy}>
              {ragBusy ? "检索中…" : "询问"}
            </button>
          </div>
          {rag && (
            <div style={{ marginTop: 14 }}>
              <div className="rag-status" data-status={rag.status}>
                {rag.status === "grounded"
                  ? "已生成（可追溯来源）"
                  : rag.status === "no_context"
                  ? "未找到相关资料"
                  : rag.status === "retrieval_ready_no_llm"
                  ? "仅检索（LLM 未配置）"
                  : rag.status === "error"
                  ? "调用失败"
                  : rag.status}
              </div>

              {rag.answer && (
                <div className="rag-answer">{rag.answer}</div>
              )}

              {rag.retrieved.length > 0 && (
                <div style={{ marginTop: 12 }}>
                  <div className="muted" style={{ fontSize: 12, marginBottom: 6 }}>
                    检索到的知识节点（来源）：
                  </div>
                  <div className="rag-sources">
                    {rag.retrieved.map((s, i) => (
                      <div key={s.id} className="rag-source">
                        <span className="rag-source-idx">{i + 1}</span>
                        <Link href={`/nodes/${s.id}`} className="rag-source-name">
                          {s.name}
                        </Link>
                        {s.source_url && (
                          <a
                            href={s.source_url}
                            target="_blank"
                            rel="noreferrer"
                            className="source-link"
                          >
                            ↗
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="note" style={{ marginTop: 10 }}>
                {rag.message}
              </div>
            </div>
          )}
        </div>
      </section>

      <section className="section">
        <h2>
          <span className="id">05</span>语义搜索{" "}
          <span className="muted" style={{ fontSize: 12, fontFamily: "var(--mono)" }}>
            （Embedding · 向量检索）
          </span>
        </h2>
        <SemanticSearch />
      </section>

      <section className="section">
        <h2>
          <span className="id">06</span>AI Agent{" "}
          <span className="muted" style={{ fontSize: 12, fontFamily: "var(--mono)" }}>
            （Tool Calling · 多步推理）
          </span>
        </h2>
        <AgentExplorer />
      </section>
    </div>
  );
}
