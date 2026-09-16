import Link from "next/link";
import { RELATION_LABELS } from "@/lib/colors";
import type { RelationOut } from "@/lib/types";

export default function RelationList({
  relations,
  selfId,
}: {
  relations: RelationOut[];
  selfId: string;
}) {
  if (!relations.length) return <p className="muted">暂无关系。</p>;

  return (
    <div>
      {relations.map((r) => {
        const isOut = r.source_id === selfId;
        const otherId = isOut ? r.target_id : r.source_id;
        const otherName = isOut ? r.target_name : r.source_name;
        return (
          <div className="rel-item" key={r.id}>
            <span className="rel-type">
              {RELATION_LABELS[r.relation_type] ?? r.relation_type}
            </span>
            <div className="rel-name">
              <Link href={`/nodes/${otherId}`}>{otherName ?? otherId}</Link>
            </div>
          </div>
        );
      })}
    </div>
  );
}
