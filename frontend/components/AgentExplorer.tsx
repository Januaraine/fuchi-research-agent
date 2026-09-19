"use client";

import { useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { CATEGORY_COLORS, CATEGORY_LABELS, FALLBACK_COLOR } from "@/lib/colors";
import type { AgentResult } from "@/lib/types";

const TOOL_LABELS: Record<string, string> = {
  vector_search: "向量检索",
  graph_search: "图遍历",
  source_retrieve: "来源检索",
  rag_answer: "RAG 问答",
};

export default function AgentExplorer() {
  const [q, setQ] = useState("");
  const [result, setResult] = useState<AgentResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    const question = q.trim();
    if (!question) return;
    setBusy(true);
    setResult(null);
    setError(null);
    try {
      setResult(await api.agentQuery(question, 6));
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="panel explorer-box">
      <div className="semantic-row">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && run()}
          placeholder="例如：ResNet 和 Transformer 在计算机视觉中的关系是什么？"
          style={{ flex: 1 }}
        />
        <button className="btn" onClick={run} disabled={busy}>
          {busy ? "探索中…" : "运行 Agent"}
        </button>
      </div>

      {error && <div className="note" style={{ color: "var(--cinnabar)" }}>{error}</div>}

      {result && (
        <div style={{ marginTop: 14 }}>
          <div className="rag-status" data-status={result.llm_used ? "grounded" : result.status}>
            {result.llm_used ? "LLM Agent" : "确定性规划（LLM 未配置）"} · {result.steps.length} 步
          </div>

          <div className="rag-answer">{result.answer}</div>

          {result.evidence.length > 0 && (
            <div style={{ marginTop: 12 }}>
              <div className="muted" style={{ fontSize: 12, marginBottom: 6 }}>
                依据的知识节点：
              </div>
              <div className="chips">
                {result.evidence.map((e) => {
                  const c = CATEGORY_COLORS[e.category] ?? FALLBACK_COLOR;
                  return (
                    <Link key={e.id} href={`/nodes/${e.id}`} className="chip" style={{ color: c, borderColor: c }}>
                      {e.name}
                    </Link>
                  );
                })}
              </div>
            </div>
          )}

          {result.steps.length > 0 && (
            <div style={{ marginTop: 14 }}>
              <div className="muted" style={{ fontSize: 12, marginBottom: 6 }}>
                执行轨迹（Tool Calling）：
              </div>
              <div className="agent-trace">
                {result.steps.map((s) => (
                  <div key={s.step} className="agent-step">
                    <span className="agent-step-idx">{s.step}</span>
                    <span className="agent-step-action">
                      {TOOL_LABELS[s.action] ?? s.action}
                    </span>
                    <span className="agent-step-args">
                      {Object.entries(s.args || {})
                        .map(([k, v]) => `${k}=${typeof v === "string" ? v : JSON.stringify(v)}`)
                        .join(" · ")}
                    </span>
                    <span className="agent-step-obs" title={s.observation}>
                      {s.observation.length > 90 ? s.observation.slice(0, 90) + "…" : s.observation}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
