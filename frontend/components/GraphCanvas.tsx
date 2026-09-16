"use client";

import { useEffect, useMemo, useState } from "react";
import { CATEGORY_COLORS, FALLBACK_COLOR } from "@/lib/colors";
import type { GraphData } from "@/lib/types";

interface Props {
  data: GraphData;
  selectedId: string | null;
  onSelect: (id: string | null) => void;
}

const W = 920;
const H = 640;

interface Pos {
  x: number;
  y: number;
}

export default function GraphCanvas({ data, selectedId, onSelect }: Props) {
  const [positions, setPositions] = useState<Record<string, Pos>>({});
  const [loading, setLoading] = useState(true);

  const degree = useMemo(() => {
    const d: Record<string, number> = {};
    data.nodes.forEach((n) => (d[n.id] = 0));
    data.edges.forEach((e) => {
      d[e.source] = (d[e.source] ?? 0) + 1;
      d[e.target] = (d[e.target] ?? 0) + 1;
    });
    return d;
  }, [data]);

  useEffect(() => {
    setLoading(true);
    const ids = data.nodes.map((n) => n.id);
    const pos: Record<string, Pos> = {};
    ids.forEach((id) => {
      pos[id] = {
        x: W / 2 + (Math.random() - 0.5) * 520,
        y: H / 2 + (Math.random() - 0.5) * 520,
      };
    });

    const ITER = 320;
    for (let it = 0; it < ITER; it++) {
      // repulsion (O(n^2))
      for (let i = 0; i < ids.length; i++) {
        for (let j = i + 1; j < ids.length; j++) {
          const a = pos[ids[i]];
          const b = pos[ids[j]];
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const d2 = dx * dx + dy * dy || 1;
          const d = Math.sqrt(d2);
          const f = 1500 / d2;
          const fx = (dx / d) * f;
          const fy = (dy / d) * f;
          a.x += fx;
          a.y += fy;
          b.x -= fx;
          b.y -= fy;
        }
      }
      // springs
      for (const e of data.edges) {
        const a = pos[e.source];
        const b = pos[e.target];
        if (!a || !b) continue;
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const d = Math.sqrt(dx * dx + dy * dy) || 0.001;
        const f = (d - 76) * 0.018;
        const fx = (dx / d) * f;
        const fy = (dy / d) * f;
        a.x += fx;
        a.y += fy;
        b.x -= fx;
        b.y -= fy;
      }
      // gravity + clamp
      for (const id of ids) {
        const p = pos[id];
        p.x += (W / 2 - p.x) * 0.03;
        p.y += (H / 2 - p.y) * 0.03;
        p.x = Math.max(24, Math.min(W - 24, p.x));
        p.y = Math.max(24, Math.min(H - 24, p.y));
      }
    }
    setPositions(pos);
    setLoading(false);
  }, [data]);

  const neighborIds = useMemo(() => {
    const s = new Set<string>();
    if (!selectedId) return s;
    data.edges.forEach((e) => {
      if (e.source === selectedId) s.add(e.target);
      if (e.target === selectedId) s.add(e.source);
    });
    return s;
  }, [selectedId, data]);

  const hasSelection = selectedId != null;

  return (
    <div className="graph-canvas">
      {loading ? (
        <div className="graph-loading">COMPUTING LAYOUT…</div>
      ) : (
        <svg
          viewBox={`0 0 ${W} ${H}`}
          style={{ width: "100%", height: "auto", display: "block" }}
        >
          <rect
            width={W}
            height={H}
            fill="transparent"
            onClick={() => onSelect(null)}
            style={{ cursor: "default" }}
          />
          {data.edges.map((e, i) => {
            const a = positions[e.source];
            const b = positions[e.target];
            if (!a || !b) return null;
            const active =
              hasSelection && (e.source === selectedId || e.target === selectedId);
            return (
              <line
                key={i}
                x1={a.x}
                y1={a.y}
                x2={b.x}
                y2={b.y}
                stroke={active ? "#c8553d" : "#2a2f37"}
                strokeWidth={active ? 1.4 : 0.6}
                opacity={hasSelection && !active ? 0.14 : 0.7}
              />
            );
          })}
          {data.nodes.map((n) => {
            const p = positions[n.id];
            if (!p) return null;
            const color = CATEGORY_COLORS[n.category] ?? FALLBACK_COLOR;
            const isSelected = n.id === selectedId;
            const isNeighbor = neighborIds.has(n.id);
            const dim = hasSelection && !isSelected && !isNeighbor;
            const r = 4 + Math.min(10, Math.sqrt(degree[n.id] ?? 0) * 1.7);
            const showLabel = isSelected || isNeighbor || (degree[n.id] ?? 0) >= 7;
            return (
              <g
                key={n.id}
                onClick={() => onSelect(n.id)}
                style={{ cursor: "pointer" }}
                opacity={dim ? 0.22 : 1}
              >
                <title>{n.name}</title>
                <circle
                  cx={p.x}
                  cy={p.y}
                  r={r}
                  fill={isSelected ? "#c8553d" : color}
                  stroke={isNeighbor ? "#e7e4dd" : "transparent"}
                  strokeWidth={isNeighbor ? 1.2 : 0}
                />
                {showLabel && (
                  <text
                    x={p.x + r + 3}
                    y={p.y + 3}
                    fontSize={isSelected ? 11 : 9}
                    fill={isSelected ? "#e7e4dd" : "#b8bdc6"}
                    fontFamily="JetBrains Mono, monospace"
                  >
                    {n.name}
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      )}
    </div>
  );
}
