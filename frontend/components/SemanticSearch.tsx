"use client";

import { useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { CATEGORY_COLORS, CATEGORY_LABELS, FALLBACK_COLOR } from "@/lib/colors";
import type { SemanticCompareOut, SemanticHit } from "@/lib/types";

function HitList({
  hits,
  showScore,
  empty,
}: {
  hits: SemanticHit[];
  showScore: boolean;
  empty: string;
}) {
  if (hits.length === 0) return <p className="muted">{empty}</p>;
  return (
    <div className="hit-list">
      {hits.map((h) => {
        const color = CATEGORY_COLORS[h.category] ?? FALLBACK_COLOR;
        return (
          <Link key={h.id} href={`/nodes/${h.id}`} className="hit-item">
            <span className="hit-name">{h.name}</span>
            <span className="hit-cat" style={{ color }}>
              {CATEGORY_LABELS[h.category] ?? h.category}
            </span>
            {showScore && <span className="hit-score">{h.score.toFixed(3)}</span>}
          </Link>
        );
      })}
    </div>
  );
}

export default function SemanticSearch() {
  const [q, setQ] = useState("");
  const [result, setResult] = useState<SemanticCompareOut | null>(null);
  const [busy, setBusy] = useState(false);
  const [buildInfo, setBuildInfo] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    const query = q.trim();
    if (!query) return;
    setBusy(true);
    setError(null);
    try {
      setResult(await api.semanticCompare(query, 8));
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  const rebuild = async () => {
    setBusy(true);
    setBuildInfo(null);
    setError(null);
    try {
      const info = await api.buildEmbeddings();
      setBuildInfo(`索引已重建：${info.built} 节点 · ${info.vocab_size} 词表`);
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
          placeholder="例如：让机器理解图像和视频的技术"
          style={{ flex: 1 }}
        />
        <button className="btn" onClick={run} disabled={busy}>
          {busy ? "检索中…" : "比较"}
        </button>
        <button className="btn ghost" onClick={rebuild} disabled={busy}>
          重建索引
        </button>
      </div>

      {buildInfo && <div className="note">{buildInfo}</div>}
      {error && <div className="note" style={{ color: "var(--cinnabar)" }}>{error}</div>}

      {result && (
        <div className="compare-grid">
          <div>
            <h3 style={{ fontSize: 13 }}>
              关键词检索 <span className="muted">（字面匹配）</span>
            </h3>
            <HitList
              hits={result.keyword}
              showScore={false}
              empty="无字面匹配结果。"
            />
          </div>
          <div>
            <h3 style={{ fontSize: 13 }}>
              语义检索 <span className="muted">（向量相似度）</span>
            </h3>
            <HitList
              hits={result.semantic}
              showScore
              empty="无语义相关结果。"
            />
          </div>
        </div>
      )}
    </div>
  );
}
