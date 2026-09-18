"use client";

import Link from "next/link";
import { CATEGORY_COLORS, CATEGORY_LABELS, FALLBACK_COLOR } from "@/lib/colors";
import type { TrendingItem } from "@/lib/types";

export default function TrendingPanel({ items }: { items: TrendingItem[] }) {
  if (items.length === 0) return <p className="muted">趋势计算中…</p>;

  const max = Math.max(1, ...items.map((i) => i.popularity));

  return (
    <div className="trending-panel">
      {items.map((item, idx) => {
        const color = CATEGORY_COLORS[item.category] ?? FALLBACK_COLOR;
        const pct = Math.max(6, Math.round((item.popularity / max) * 100));
        return (
          <Link key={item.id} href={`/nodes/${item.id}`} className="trending-item">
            <span className="trending-rank">{String(idx + 1).padStart(2, "0")}</span>
            <div className="trending-main">
              <div className="trending-head">
                <span className="trending-name">{item.name}</span>
                <span className="trending-cat" style={{ color }}>
                  {CATEGORY_LABELS[item.category] ?? item.category}
                </span>
              </div>
              <div className="trending-bar">
                <div
                  className="trending-fill"
                  style={{ width: `${pct}%`, background: color }}
                />
              </div>
            </div>
            <span className="trending-score">{item.popularity.toFixed(1)}</span>
          </Link>
        );
      })}
    </div>
  );
}
