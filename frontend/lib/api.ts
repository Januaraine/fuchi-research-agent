import type {
  GraphData,
  NodeDetail,
  NodeSummary,
  RagResult,
  Stats,
} from "./types";

const BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${path}`);
  return res.json() as Promise<T>;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${path}`);
  return res.json() as Promise<T>;
}

export const api = {
  stats: () => get<Stats>("/api/stats"),
  categories: () => get<{ category: string; count: number }[]>("/api/categories"),
  nodes: (opts?: { category?: string; q?: string; limit?: number }) => {
    const p = new URLSearchParams();
    if (opts?.category) p.set("category", opts.category);
    if (opts?.q) p.set("q", opts.q);
    if (opts?.limit) p.set("limit", String(opts.limit));
    const qs = p.toString();
    return get<NodeSummary[]>(`/api/nodes${qs ? `?${qs}` : ""}`);
  },
  node: (id: string) => get<NodeDetail>(`/api/nodes/${encodeURIComponent(id)}`),
  graph: (nodeId?: string) =>
    get<GraphData>(`/api/graph${nodeId ? `?node_id=${encodeURIComponent(nodeId)}` : ""}`),
  search: (q: string) =>
    get<NodeSummary[]>(`/api/search?q=${encodeURIComponent(q)}`),
  ragQuery: (question: string) =>
    post<RagResult>("/api/rag/query", { question }),
};
