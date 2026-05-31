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
    "rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 " +
    "enabled:hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40";

  return (
    <div className="flex items-center justify-between gap-4">
      <p className="text-sm text-gray-500">
        Showing <span className="font-medium text-gray-700">{start}</span>–
        <span className="font-medium text-gray-700">{end}</span> of{" "}
        <span className="font-medium text-gray-700">{total}</span>
      </p>
      <div className="flex gap-2">
        <button
          type="button"
          className={buttonClass}
          disabled={!hasPrev}
          onClick={() => onChange(Math.max(0, offset - limit))}
        >
          ← Previous
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
