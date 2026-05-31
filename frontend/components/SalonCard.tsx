import Link from "next/link";

import { RatingStars } from "@/components/RatingStars";
import { ServiceTags } from "@/components/ServiceTags";
import type { SalonSummary } from "@/lib/types";

/** A clickable summary card linking to the salon's detail page. */
export function SalonCard({ salon }: { salon: SalonSummary }) {
  return (
    <Link
      href={`/salons/${salon.id}`}
      className="group flex flex-col gap-3 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm transition hover:border-rose-200 hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className="font-semibold text-gray-900 group-hover:text-rose-700">{salon.name}</h3>
        {salon.price_range && (
          <span className="shrink-0 text-sm font-medium text-emerald-600">
            {salon.price_range}
          </span>
        )}
      </div>

      <div className="flex items-center justify-between">
        <span className="inline-flex items-center gap-1 text-sm text-gray-500">
          <span aria-hidden>📍</span>
          {salon.district}
        </span>
        <RatingStars rating={salon.rating} reviewCount={salon.review_count} />
      </div>

      <ServiceTags services={salon.services} />
    </Link>
  );
}
