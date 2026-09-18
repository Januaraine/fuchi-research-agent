"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { useRealtime } from "@/lib/useRealtime";
import {
  CATEGORY_COLORS,
  CATEGORY_LABELS,
  FALLBACK_COLOR,
  RELATION_LABELS,
} from "@/lib/colors";
import GraphCanvas from "@/components/GraphCanvas";
import type { GraphData, NodeDetail, NodeSummary } from "@/lib/types";

const RELATION_TYPES = [
  "subfield_of",
  "is_a",
  "part_of",
  "used_in",
  "based_on",
  "related_to",
];

function mergeGraph(base: GraphData, add: GraphData): GraphData {
  const nodeMap = new Map(base.nodes.map((n) => [n.id, n]));
  add.nodes.forEach((n) => nodeMap.set(n.id, n));
  const edgeKeys = new Set(base.edges.map((e) => `${e.source}|${e.target}|${e.relation_type}`));
  const edges = [...base.edges];
  add.edges.forEach((e) => {
    const k = `${e.source}|${e.target}|${e.relation_type}`;
    if (!edgeKeys.has(k)) {
      edgeKeys.add(k);
      edges.push(e);
    }
  });
  return { nodes: [...nodeMap.values()], edges };
}

export default function GraphPage() {
  const [graph, setGraph] = useState<GraphData | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<NodeDetail | null>(null);
  const [results, setResults] = useState<NodeSummary[]>([]);
  const [term, setTerm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [hiddenTypes, setHiddenTypes] = useState<string[]>([]);
  const [focused, setFocused] = useState(false);

  const { connected, events } = useRealtime(40);

  useEffect(() => {
    api.graph()
      .then(setGraph)
      .catch((e) => setError(String(e)));

    const q = new URLSearchParams(window.location.search).get("q") ?? "";
    setTerm(q);
    if (q) runSearch(q);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!selectedId) {
      setDetail(null);
      return;
    }
    let alive = true;
    api.node(selectedId)
      .then((d) => alive && setDetail(d))
      .catch(() => alive && setDetail(null));
    return () => {
      alive = false;
    };
  }, [selectedId]);

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

  const loadFull = () => {
    setFocused(false);
    api.graph()
      .then(setGraph)
      .catch((e) => setError(String(e)));
  };

  const focus = (id: string) => {
    setSelectedId(id);
    setFocused(true);
    api.graph(id, 2)
      .then(setGraph)
      .catch((e) => setError(String(e)));
  };

  const expand = (id: string) => {
    api.neighbors(id)
      .then((nb) => setGraph((g) => (g ? mergeGraph(g, nb) : nb)))
      .catch(() => {});
  };

  const selectResult = (id: string) => {
    setSelectedId(id);
    focus(id);
  };

  const toggleType = (t: string) =>
    setHiddenTypes((h) => (h.includes(t) ? h.filter((x) => x !== t) : [...h, t]));

  // 最近一段时间收到活动事件的节点，用于在图中打「呼吸」光环。
  const activeIds = useMemo(() => {
    const ids: string[] = [];
    for (let i = events.length - 1; i >= 0; i--) {
      const id = events[i].data?.node_id;
      if (id && !ids.includes(id)) ids.push(id);
      if (ids.length >= 6) break;
    }
    return ids;
  }, [events]);

  if (error)
    return <div className="shell state">无法连接后端 API：{error}</div>;

  const color = detail ? CATEGORY_COLORS[detail.category] ?? FALLBACK_COLOR : FALLBACK_COLOR;

  return (
    <div className="shell" style={{ paddingTop: 24, paddingBottom: 48 }}>
      <div style={{ marginBottom: 16, display: "flex", alignItems: "flex-end", gap: 16 }}>
        <div style={{ flex: 1 }}>
          <h2 style={{ margin: 0 }}>
            <span className="id">GRAPH</span>知识图谱
          </h2>
          <p className="muted" style={{ margin: "6px 0 0" }}>
            点击节点选中；「聚焦」显示邻域子图，「展开邻居」增量补充关系，下方可筛选关系类型。
          </p>
        </div>
        <div className={`live-badge ${connected ? "on" : "off"}`}>
          <span className="live-dot" />
          {connected ? "LIVE" : "OFFLINE"}
        </div>
      </div>

      {/* 关系类型筛选 */}
      <div className="filter-row">
        {RELATION_TYPES.map((t) => {
          const off = hiddenTypes.includes(t);
          return (
            <button
              key={t}
              className={`filter-chip ${off ? "off" : ""}`}
              onClick={() => toggleType(t)}
            >
              {RELATION_LABELS[t] ?? t}
            </button>
          );
        })}
        <span className="muted" style={{ fontSize: 12, marginLeft: "auto" }}>
          {hiddenTypes.length > 0 ? `已隐藏 ${hiddenTypes.length} 类关系` : "显示全部关系"}
        </span>
      </div>

      <div className="graph-layout">
        <div>
          {graph ? (
            <GraphCanvas
              data={graph}
              selectedId={selectedId}
              onSelect={setSelectedId}
              hiddenTypes={hiddenTypes}
              activeIds={activeIds}
            />
          ) : (
            <div className="graph-canvas">
              <div className="graph-loading">LOADING…</div>
            </div>
          )}
          <div className="toolbar">
            <button className="btn ghost" onClick={loadFull} disabled={!focused && graph != null}>
              重置为全图
            </button>
            <span className="muted" style={{ fontSize: 12 }}>
              {graph ? `${graph.nodes.length} 节点 · ${graph.edges.length} 关系` : ""}
            </span>
          </div>
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
              {results.length === 0 && (
                <p className="muted">输入关键词搜索知识节点，点击结果可定位到图中。</p>
              )}
              {results.map((r) => (
                <div
                  key={r.id}
                  className={`result-item ${r.id === selectedId ? "active" : ""}`}
                  onClick={() => selectResult(r.id)}
                >
                  <span className="name">{r.name}</span>
                  <span className="muted" style={{ fontSize: 11, marginLeft: 8 }}>
                    {CATEGORY_LABELS[r.category] ?? r.category}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="panel" style={{ marginTop: 16 }}>
            <h3>节点详情</h3>
            {detail ? (
              <div>
                <span
                  className="badge"
                  style={{ color, borderColor: color }}
                >
                  {CATEGORY_LABELS[detail.category] ?? detail.category}
                </span>
                <h3 style={{ marginTop: 8 }}>{detail.name}</h3>
                <p className="muted" style={{ fontSize: 12.5, lineHeight: 1.6 }}>
                  {detail.description}
                </p>

                <div className="detail-actions">
                  <button className="btn" onClick={() => focus(detail.id)}>
                    聚焦
                  </button>
                  <button className="btn ghost" onClick={() => expand(detail.id)}>
                    展开邻居
                  </button>
                  <Link href={`/nodes/${detail.id}`} className="btn ghost">
                    完整资料 →
                  </Link>
                </div>

                <div className="rel-stats">
                  <span>出 {detail.outgoing.length}</span>
                  <span>入 {detail.incoming.length}</span>
                  <span>相关 {detail.related.length}</span>
                </div>

                {detail.related.length > 0 && (
                  <div className="chips" style={{ marginTop: 8 }}>
                    {detail.related.map((n) => (
                      <button
                        key={n.id}
                        className="chip chip-btn"
                        onClick={() => focus(n.id)}
                      >
                        {n.name}
                      </button>
                    ))}
                  </div>
                )}
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
