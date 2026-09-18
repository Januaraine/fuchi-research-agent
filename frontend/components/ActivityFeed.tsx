"use client";

import Link from "next/link";
import { RELATION_LABELS } from "@/lib/colors";
import type { RealtimeEvent } from "@/lib/types";

function formatTime(ts: number): string {
  const d = new Date(ts * 1000);
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  const ss = String(d.getSeconds()).padStart(2, "0");
  return `${hh}:${mm}:${ss}`;
}

interface Desc {
  text: string;
  nodeId?: string;
  kind: "user" | "knowledge" | "trend" | "system";
}

function describe(event: RealtimeEvent): Desc {
  const d = event.data ?? {};
  switch (event.type) {
    case "user_activity": {
      const action =
        d.action === "explored" ? "探索了" : d.action === "searched" ? "搜索了" : "打开了";
      return { text: `${d.user_id} ${action}「${d.name}」`, nodeId: d.node_id, kind: "user" };
    }
    case "node_activity":
      return {
        text: `知识活动：${d.name} 活跃度 +${d.activity_delta}`,
        nodeId: d.node_id,
        kind: "knowledge",
      };
    case "trending_update":
      return { text: "趋势热度已重算", kind: "trend" };
    case "system_status":
      return { text: d.message ?? "系统状态更新", kind: "system" };
    case "node_created":
      return {
        text: `新节点「${d.node?.name ?? d.name ?? "?"}」加入知识网络`,
        nodeId: d.node?.id ?? d.node_id,
        kind: "knowledge",
      };
    case "relation_created":
      return {
        text: `新关系：${d.source_name} → ${d.target_name}（${RELATION_LABELS[d.relation_type] ?? d.relation_type}）`,
        nodeId: d.source_id,
        kind: "knowledge",
      };
    default:
      return { text: event.type, kind: "system" };
  }
}

export default function ActivityFeed({
  events,
  empty = "等待实时事件…",
}: {
  events: RealtimeEvent[];
  empty?: string;
}) {
  if (events.length === 0) return <p className="muted">{empty}</p>;

  return (
    <div className="activity-feed">
      {events.map((e, i) => {
        const d = describe(e);
        const body = (
          <>
            <span className="feed-dot" data-kind={d.kind} />
            <span className="feed-text">{d.text}</span>
            <span className="feed-time">{formatTime(e.ts)}</span>
          </>
        );
        return d.nodeId ? (
          <Link key={`${e.ts}-${i}`} href={`/nodes/${d.nodeId}`} className="feed-item">
            {body}
          </Link>
        ) : (
          <div key={`${e.ts}-${i}`} className="feed-item">
            {body}
          </div>
        );
      })}
    </div>
  );
}
