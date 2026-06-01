"use client";

import Link from "next/link";
import useSWR from "swr";

import { SalonCard } from "@/components/SalonCard";
import { listSalons } from "@/lib/api";

/**
 * A restrained taste of the catalogue on the hero page — three salons and a
 * link into the full directory. Stays quiet so the prompt bar leads; renders
 * nothing if the API is unavailable.
 */
export function TrendingStrip() {
  const { data, isLoading, error } = useSWR("trending", () => listSalons({ limit: 3 }));

  if (error) return null;

  return (
    <section className="mx-auto w-full max-w-6xl px-6 pb-24">
      <div className="mb-5 flex items-end justify-between">
        <h2 className="font-mono text-[11px] uppercase tracking-[0.28em] text-ash-dim">
          Fresh in the directory
        </h2>
        <Link
          href="/browse"
          className="font-mono text-[11px] uppercase tracking-[0.18em] text-ash transition-colors hover:text-neon-soft"
        >
          Browse all →
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {isLoading || !data
          ? Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="shimmer h-44 rounded-2xl" />
            ))
          : data.items.map((salon, i) => (
              <div key={salon.id} className="rise" style={{ animationDelay: `${i * 80}ms` }}>
                <SalonCard salon={salon} />
              </div>
            ))}
      </div>
    </section>
  );
}
