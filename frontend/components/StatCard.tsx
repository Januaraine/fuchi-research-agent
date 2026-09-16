export default function StatCard({
  label,
  value,
  dim,
}: {
  label: string;
  value: string | number;
  dim?: string;
}) {
  return (
    <div className="stat-card">
      <div className="label">{label}</div>
      <div className="value">
        {value}
        {dim ? <span className="dim"> {dim}</span> : null}
      </div>
    </div>
  );
}
