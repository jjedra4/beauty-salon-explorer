"use client";

import { Children, useEffect, useState } from "react";

/**
 * Lightweight Pinterest-style masonry.
 *
 * Distributes children round-robin into N equal-width flex columns. Unlike CSS
 * `columns`, items stay in **normal flow**, so transforms (hover lift, the
 * staggered entrance animation) paint and hit-test correctly — CSS multicol
 * mis-renders transformed/filtered children, leaving the card painted in one
 * place but clickable in another.
 *
 * Column count is responsive (recomputed on resize). SSR and the first client
 * render both use `columns.lg`, so there's no hydration mismatch; the count is
 * corrected on mount.
 */
export function Masonry({
  children,
  gap = "gap-4",
  columns = { base: 1, sm: 2, lg: 3 },
}: {
  children: React.ReactNode;
  gap?: string;
  columns?: { base: number; sm: number; lg: number };
}) {
  const { base, sm, lg } = columns;
  const [cols, setCols] = useState(lg);

  useEffect(() => {
    const compute = () => {
      const w = window.innerWidth;
      setCols(w >= 1024 ? lg : w >= 640 ? sm : base);
    };
    compute();
    window.addEventListener("resize", compute);
    return () => window.removeEventListener("resize", compute);
  }, [base, sm, lg]);

  const items = Children.toArray(children);
  // Never leave empty columns when there are fewer items than columns.
  const colCount = Math.max(1, Math.min(cols, items.length || 1));
  const buckets: React.ReactNode[][] = Array.from({ length: colCount }, () => []);
  items.forEach((child, i) => buckets[i % colCount].push(child));

  return (
    <div className={`flex items-start ${gap}`}>
      {buckets.map((bucket, i) => (
        <div key={i} className={`flex min-w-0 flex-1 flex-col ${gap}`}>
          {bucket}
        </div>
      ))}
    </div>
  );
}
