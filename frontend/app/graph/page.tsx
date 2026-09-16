"use client";

import { useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import { CATEGORY_COLORS, CATEGORY_LABELS, FALLBACK_COLOR } from "@/lib/colors";
import GraphCanvas from "@/components/GraphCanvas";
import type { GraphData, NodeSummary } from "@/lib/types";

export default function GraphPage() {
  const [data, setData] = useState<GraphData | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [results, setResults] = useState<NodeSummary[]>([]);
  const [term, setTerm] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.graph()
      .then(setData)
      .catch((e) => setError(String(e)));

    const q = new URLSearchParams(window.location.search).get("q") ?? "";
    setTerm(q);
    if (q) runSearch(q);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const runSearch = (t: string) => {
    const v = t.trim();
    if (!v) {
      setResults([]);
      return;
    }
    api.search(v)
      .then(setResults)
      .catch(() => setResults([]));
  };

  const selectedNode = useMemo(
    () => data?.nodes.find((n) => n.id === selectedId) ?? null,
    [data, selectedId]
  );

  if (error)
    return <div className="shell state">无法连接后端 API：{error}</div>;

  return (
    <div className="shell" style={{ paddingTop: 24, paddingBottom: 48 }}>
      <div style={{ marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>
          <span className="id">GRAPH</span>知识图谱
        </h2>
        <p className="muted" style={{ margin: "6px 0 0" }}>
          点击节点查看详情，再次点击空白处取消选择。
        </p>
      </div>

      <div className="graph-layout">
        <div>
          {data ? (
            <GraphCanvas data={data} selectedId={selectedId} onSelect={setSelectedId} />
          ) : (
            <div className="graph-canvas">
              <div className="graph-loading">LOADING…</div>
            </div>
          )}
        </div>

        <div>
          <div className="panel">
            <h3>搜索</h3>
            <form
              className="search-box"
              onSubmit={(e) => {
                e.preventDefault();
                runSearch(term);
              }}
            >
              <input
                value={term}
                onChange={(e) => setTerm(e.target.value)}
                placeholder="搜索…"
                style={{ width: "100%" }}
              />
              <button type="submit">搜索</button>
            </form>
            <div style={{ marginTop: 12 }}>
              {results.length === 0 && <p className="muted">输入关键词搜索知识节点。</p>}
              {results.map((r) => (
                <div
                  key={r.id}
                  className={`result-item ${r.id === selectedId ? "active" : ""}`}
                  onClick={() => setSelectedId(r.id)}
                >
                  <span className="name">{r.name}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="panel" style={{ marginTop: 16 }}>
            <h3>节点详情</h3>
            {selectedNode ? (
              <div>
                <span
                  className="badge"
                  style={{
                    color: CATEGORY_COLORS[selectedNode.category] ?? FALLBACK_COLOR,
                    borderColor: CATEGORY_COLORS[selectedNode.category] ?? FALLBACK_COLOR,
                  }}
                >
                  {CATEGORY_LABELS[selectedNode.category] ?? selectedNode.category}
                </span>
                <h3 style={{ marginTop: 8 }}>{selectedNode.name}</h3>
                <a href={`/nodes/${selectedNode.id}`} className="source-link">
                  查看完整资料 →
                </a>
              </div>
            ) : (
              <p className="muted">点击图中节点查看详情。</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
