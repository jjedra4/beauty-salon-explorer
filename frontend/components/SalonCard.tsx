import Link from "next/link";

import { RatingStars } from "@/components/RatingStars";
import { ServiceTags } from "@/components/ServiceTags";
import type { SalonSummary } from "@/lib/types";

/** A clickable summary card linking to the salon's detail page. */
export function SalonCard({ salon }: { salon: SalonSummary }) {
  return (
    <Link
      href={`/salons/${salon.id}`}
      className="glass group relative flex flex-col gap-3 overflow-hidden rounded-2xl p-5 transition duration-300 hover:-translate-y-1 hover:border-neon/40 hover:shadow-[0_0_40px_-18px_rgba(255,77,109,0.6)]"
    >
      {/* Accent edge that lights up on hover. */}
      <span className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-neon/60 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />

      <div className="flex items-start justify-between gap-3">
        <h3 className="font-display text-lg leading-snug text-porcelain transition-colors group-hover:text-neon-soft">
          {salon.name}
        </h3>
        {salon.price_range && (
          <span className="shrink-0 font-mono text-sm text-gold">{salon.price_range}</span>
        )}
      </div>

      <div className="flex items-center justify-between">
        <span className="inline-flex items-center gap-1.5 font-mono text-xs uppercase tracking-[0.12em] text-ash">
          <DotIcon /> {salon.district}
        </span>
        <RatingStars rating={salon.rating} reviewCount={salon.review_count} />
      </div>

      <ServiceTags services={salon.services} />
    </Link>
  );
}

function DotIcon() {
  return (
    <span
      aria-hidden
      className="inline-block h-1.5 w-1.5 rounded-full bg-neon shadow-[0_0_6px_rgba(255,77,109,0.8)]"
    />
  );
}
