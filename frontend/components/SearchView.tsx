"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import useSWR from "swr";

import { ModeBadge } from "@/components/ModeBadge";
import { PromptSearch } from "@/components/PromptSearch";
import { SalonTile } from "@/components/SalonTile";
import { StateMessage } from "@/components/StateMessage";
import { searchSalons } from "@/lib/api";

/**
 * Search results experience. Reads the query from `?q=` (so results are
 * shareable and the back button works), fetches `/salons/search` with SWR, and
 * lays out large result tiles. A compact prompt bar stays on top to refine.
 *
 * Reads `useSearchParams`, so it must render inside a `<Suspense>` boundary.
 */
export function SearchView() {
  const query = (useSearchParams().get("q") ?? "").trim();
  const { data, error, isLoading } = useSWR(
    query ? ["search", query] : null,
    () => searchSalons(query),
    { keepPreviousData: true },
  );

  // Normalise scores into a 0–1 relevance bar, robust to whatever scale the
  // backend returns (cosine similarity, distance-derived, etc.).
  const maxScore = data?.items.reduce((m, s) => Math.max(m, s.score), 0) ?? 0;

  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-6 py-10">
      <div className="rise flex flex-col gap-6">
        <Link
          href="/"
          className="font-mono text-[11px] uppercase tracking-[0.18em] text-ash transition-colors hover:text-neon-soft"
        >
          ← Discover
        </Link>
        <PromptSearch size="compact" />
      </div>

      <div className="mt-8">
        {!query ? (
          <StateMessage
            title="Describe a salon to begin"
            description="For example: “barber for a skin fade in Praga, open late”."
          />
        ) : error ? (
          <StateMessage
            tone="error"
            title="Search failed"
            description="Make sure the backend is running, then try again."
          />
        ) : isLoading && !data ? (
          <Searching query={query} />
        ) : !data ? null : (
          <>
            <header className="rise mb-6 flex flex-wrap items-center justify-between gap-3">
              <p className="font-display text-xl text-porcelain">
                {data.items.length} result{data.items.length === 1 ? "" : "s"}
                <span className="text-ash"> for </span>
                <span className="neon-text italic">“{query}”</span>
              </p>
              <ModeBadge mode={data.mode} />
            </header>

            {data.items.length === 0 ? (
              <StateMessage
                title="No matches"
                description="Try rephrasing, or browse the full directory."
              />
            ) : (
              <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
                {data.items.map((salon, i) => (
                  <div key={salon.id} className="rise" style={{ animationDelay: `${i * 60}ms` }}>
                    <SalonTile
                      salon={salon}
                      rank={i + 1}
                      relevance={maxScore > 0 ? salon.score / maxScore : null}
                      mode={data.mode}
                    />
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}

function Searching({ query }: { query: string }) {
  return (
    <div className="flex flex-col gap-5">
      <p className="caret font-mono text-sm text-ash">
        Searching the atelier for <span className="text-neon-soft">{query}</span>
      </p>
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="shimmer h-56 rounded-3xl" />
        ))}
      </div>
    </div>
  );
}
