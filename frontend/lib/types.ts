export interface NodeSummary {
  id: string;
  name: string;
  category: string;
  description: string;
  source: string | null;
  source_url: string | null;
  popularity: number;
}

export interface RelationOut {
  id: number;
  source_id: string;
  target_id: string;
  relation_type: string;
  source_name: string | null;
  source_category: string | null;
  target_name: string | null;
  target_category: string | null;
}

export interface NodeDetail extends NodeSummary {
  outgoing: RelationOut[];
  incoming: RelationOut[];
  related: NodeSummary[];
}

export interface GraphNode {
  id: string;
  name: string;
  category: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  relation_type: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface Stats {
  nodes: number;
  relations: number;
  categories: Record<string, number>;
}

export interface RagSource {
  id: string;
  name: string;
  category: string;
  score: number;
}

export interface RagResult {
  question: string;
  status: string;
  message: string;
  answer: string | null;
  retrieved: RagSource[];
  context: string | null;
}
