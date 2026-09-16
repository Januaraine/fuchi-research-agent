"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { CATEGORY_COLORS, CATEGORY_LABELS, FALLBACK_COLOR } from "@/lib/colors";
import NodeCard from "@/components/NodeCard";
import RelationList from "@/components/RelationList";
import type { NodeDetail } from "@/lib/types";

export default function NodeDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [node, setNode] = useState<NodeDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.node(id)
      .then(setNode)
      .catch((e) => setError(String(e)));
  }, [id]);

  if (error) return <div className="shell state">加载失败：{error}</div>;
  if (!node) return <div className="shell state">加载中…</div>;

  const color = CATEGORY_COLORS[node.category] ?? FALLBACK_COLOR;

  return (
    <div className="shell" style={{ paddingBottom: 48 }}>
      <div className="detail-head">
        <span className="badge" style={{ color, borderColor: color }}>
          {CATEGORY_LABELS[node.category] ?? node.category}
        </span>
        <h1>{node.name}</h1>
        <p className="detail-desc">{node.description}</p>
        {node.source && node.source_url && (
          <p>
            <a
              className="source-link"
              href={node.source_url}
              target="_blank"
              rel="noreferrer"
            >
              来源：{node.source} ↗
            </a>
          </p>
        )}
      </div>

      <section className="section">
        <h2>
          <span className="id">OUT</span>指向的关系（{node.outgoing.length}）
        </h2>
        <RelationList relations={node.outgoing} selfId={node.id} />
      </section>

      <section className="section">
        <h2>
          <span className="id">IN</span>指入的关系（{node.incoming.length}）
        </h2>
        <RelationList relations={node.incoming} selfId={node.id} />
      </section>

      {node.related.length > 0 && (
        <section className="section">
          <h2>
            <span className="id">REL</span>相关知识
          </h2>
          <div className="node-grid">
            {node.related.map((n) => (
              <NodeCard key={n.id} node={n} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
