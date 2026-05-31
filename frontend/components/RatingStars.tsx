/** Compact rating display: a star, the score, and the review count. */
export function RatingStars({
  rating,
  reviewCount,
}: {
  rating: number | null;
  reviewCount: number | null;
}) {
  if (rating === null) {
    return <span className="text-sm text-gray-400">No rating</span>;
  }
  return (
    <span className="inline-flex items-center gap-1 text-sm font-medium text-gray-700">
      <span className="text-amber-500" aria-hidden>
        ★
      </span>
      {rating.toFixed(1)}
      {reviewCount !== null && (
        <span className="font-normal text-gray-400">({reviewCount})</span>
      )}
    </span>
  );
}
