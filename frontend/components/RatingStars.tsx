/** Compact rating display: a gold star, the score, and the review count. */
export function RatingStars({
  rating,
  reviewCount,
}: {
  rating: number | null;
  reviewCount: number | null;
}) {
  if (rating === null) {
    return <span className="font-mono text-xs uppercase tracking-wider text-ash-dim">Unrated</span>;
  }
  return (
    <span className="inline-flex items-baseline gap-1.5 font-mono text-sm text-porcelain">
      <span className="text-gold drop-shadow-[0_0_6px_rgba(241,178,74,0.5)]" aria-hidden>
        ★
      </span>
      <span className="font-bold">{rating.toFixed(1)}</span>
      {reviewCount !== null && <span className="text-xs text-ash-dim">/ {reviewCount}</span>}
    </span>
  );
}
