/** Previous/next pagination with a "showing X–Y of N" summary. */
export function Pagination({
  total,
  limit,
  offset,
  onChange,
}: {
  total: number;
  limit: number;
  offset: number;
  onChange: (offset: number) => void;
}) {
  if (total <= limit) return null;

  const start = offset + 1;
  const end = Math.min(offset + limit, total);
  const hasPrev = offset > 0;
  const hasNext = end < total;

  const buttonClass =
    "rounded-xl border border-line bg-ink-2/60 px-4 py-2 font-mono text-xs uppercase " +
    "tracking-[0.14em] text-porcelain transition enabled:hover:border-neon/50 " +
    "enabled:hover:text-neon-soft disabled:cursor-not-allowed disabled:opacity-30";

  return (
    <div className="flex items-center justify-between gap-4 pt-2">
      <p className="font-mono text-xs text-ash-dim">
        <span className="text-porcelain">{start}</span>–
        <span className="text-porcelain">{end}</span> of{" "}
        <span className="text-porcelain">{total}</span>
      </p>
      <div className="flex gap-2">
        <button
          type="button"
          className={buttonClass}
          disabled={!hasPrev}
          onClick={() => onChange(Math.max(0, offset - limit))}
        >
          ← Prev
        </button>
        <button
          type="button"
          className={buttonClass}
          disabled={!hasNext}
          onClick={() => onChange(offset + limit)}
        >
          Next →
        </button>
      </div>
    </div>
  );
}
