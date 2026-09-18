import type {
  GraphData,
  NodeDetail,
  NodeSummary,
  RagResult,
  RecommendOut,
  SemanticBuildOut,
  SemanticCompareOut,
  SemanticSearchOut,
  Stats,
} from "./types";

const BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

export const WS_URL =
  (process.env.NEXT_PUBLIC_WS_BASE ?? BASE.replace(/^http/, "ws")) + "/api/ws";

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
  graph: (nodeId?: string, depth?: number) => {
    const p = new URLSearchParams();
    if (nodeId) p.set("node_id", nodeId);
    if (depth != null) p.set("depth", String(depth));
    const qs = p.toString();
    return get<GraphData>(`/api/graph${qs ? `?${qs}` : ""}`);
  },
  neighbors: (nodeId: string) =>
    get<GraphData>(`/api/graph/neighbors/${encodeURIComponent(nodeId)}`),
  search: (q: string) =>
    get<NodeSummary[]>(`/api/search?q=${encodeURIComponent(q)}`),
  ragQuery: (question: string) =>
    post<RagResult>("/api/rag/query", { question }),
  semanticSearch: (q: string, limit?: number) =>
    get<SemanticSearchOut>(
      `/api/semantic/search?q=${encodeURIComponent(q)}${limit ? `&limit=${limit}` : ""}`
    ),
  semanticCompare: (q: string, limit?: number) =>
    get<SemanticCompareOut>(
      `/api/semantic/compare?q=${encodeURIComponent(q)}${limit ? `&limit=${limit}` : ""}`
    ),
  semanticRecommend: (id: string, limit?: number) =>
    get<RecommendOut>(
      `/api/semantic/recommend/${encodeURIComponent(id)}${limit ? `?limit=${limit}` : ""}`
    ),
  buildEmbeddings: () => post<SemanticBuildOut>("/api/semantic/build", {}),
};
