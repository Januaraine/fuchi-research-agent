import Link from "next/link";
import { CATEGORY_COLORS, CATEGORY_LABELS, FALLBACK_COLOR } from "@/lib/colors";
import type { NodeSummary } from "@/lib/types";

export default function NodeCard({ node }: { node: NodeSummary }) {
  const color = CATEGORY_COLORS[node.category] ?? FALLBACK_COLOR;
  return (
    <Link href={`/nodes/${node.id}`} className="node-card">
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: 8,
        }}
      >
        <span className="name">{node.name}</span>
        <span className="badge" style={{ color, borderColor: color }}>
          {CATEGORY_LABELS[node.category] ?? node.category}
        </span>
      </div>
      <p className="desc">{node.description}</p>
    </Link>
  );
}
