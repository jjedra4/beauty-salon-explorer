import Link from "next/link";

import { RatingStars } from "@/components/RatingStars";
import { ServiceTags } from "@/components/ServiceTags";
import type { SalonSearchResult, SearchMode } from "@/lib/types";

/**
 * The large result tile used on the search page. Shows more than the compact
 * browse card: a rank index, a relevance meter (for semantic results), the full
 * spread of services, and a clear call to open the detail view.
 */
export function SalonTile({
  salon,
  rank,
  relevance,
  mode,
}: {
  salon: SalonSearchResult;
  rank: number;
  relevance: number | null;
  mode: SearchMode;
}) {
  return (
    <Link
      href={`/salons/${salon.id}`}
      className="glass group relative flex flex-col gap-5 overflow-hidden rounded-3xl p-7 transition duration-300 hover:-translate-y-1 hover:border-neon/40 hover:shadow-[0_0_60px_-22px_rgba(255,77,109,0.65)]"
    >
      <span className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-neon/60 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />

      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-4">
          <span className="font-mono text-xs leading-none text-ash-dim">
            {String(rank).padStart(2, "0")}
          </span>
          <div>
            <h3 className="font-display text-2xl leading-tight text-porcelain transition-colors group-hover:text-neon-soft">
              {salon.name}
            </h3>
            <p className="mt-1.5 inline-flex items-center gap-1.5 font-mono text-xs uppercase tracking-[0.14em] text-ash">
              <span className="inline-block h-1.5 w-1.5 rounded-full bg-neon shadow-[0_0_6px_rgba(255,77,109,0.8)]" />
              {salon.district}
            </p>
          </div>
        </div>
        {salon.price_range && (
          <span className="shrink-0 font-mono text-base text-gold">{salon.price_range}</span>
        )}
      </div>

      {mode === "semantic" && relevance !== null && (
        <div className="flex items-center gap-3">
          <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-ash-dim">
            Match
          </span>
          <span className="h-1 flex-1 overflow-hidden rounded-full bg-ink-3">
            <span
              className="block h-full rounded-full bg-gradient-to-r from-neon-deep to-neon shadow-[0_0_10px_rgba(255,77,109,0.7)]"
              style={{ width: `${Math.round(relevance * 100)}%` }}
            />
          </span>
          <span className="font-mono text-[10px] text-neon-soft">
            {Math.round(relevance * 100)}%
          </span>
        </div>
      )}

      <div className="flex items-center justify-between gap-4 border-t border-line/50 pt-4">
        <RatingStars rating={salon.rating} reviewCount={salon.review_count} />
        <span className="font-mono text-xs text-ash transition-colors group-hover:text-neon-soft">
          View →
        </span>
      </div>

      <ServiceTags services={salon.services} max={6} />
    </Link>
  );
}
