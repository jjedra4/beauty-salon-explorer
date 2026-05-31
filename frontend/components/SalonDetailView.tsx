"use client";

import Link from "next/link";
import { useState } from "react";
import useSWR from "swr";

import { EditSalonForm } from "@/components/EditSalonForm";
import { RatingStars } from "@/components/RatingStars";
import { ServiceTags } from "@/components/ServiceTags";
import { StateMessage } from "@/components/StateMessage";
import { ApiError, getSalon } from "@/lib/api";

/** Salon detail view with an inline edit mode (persists via the API). */
export function SalonDetailView({ salonId }: { salonId: number }) {
  const [editing, setEditing] = useState(false);
  const { data: salon, error, isLoading, mutate } = useSWR(
    Number.isFinite(salonId) ? ["salon", salonId] : null,
    () => getSalon(salonId),
  );

  if (isLoading) {
    return (
      <DetailShell>
        <StateMessage title="Loading salon…" />
      </DetailShell>
    );
  }

  if (error) {
    const notFound = error instanceof ApiError && error.status === 404;
    return (
      <DetailShell>
        <StateMessage
          tone="error"
          title={notFound ? "Salon not found" : "Couldn't load this salon"}
          description={notFound ? "It may have been removed." : "Please try again later."}
        />
      </DetailShell>
    );
  }

  if (!salon) return null;

  if (editing) {
    return (
      <DetailShell>
        <EditSalonForm
          salon={salon}
          onSaved={(updated) => {
            // Update the cached salon without a refetch, then exit edit mode.
            void mutate(updated, { revalidate: false });
            setEditing(false);
          }}
          onCancel={() => setEditing(false)}
        />
      </DetailShell>
    );
  }

  const mapsHref = salon.latitude
    ? `https://www.google.com/maps/search/?api=1&query=${salon.latitude},${salon.longitude}`
    : `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(salon.address)}`;

  return (
    <DetailShell>
      <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white">
        <div className="flex flex-col gap-3 border-b border-gray-100 p-6">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <h1 className="text-2xl font-bold text-gray-900">{salon.name}</h1>
            <div className="flex items-center gap-3">
              {salon.price_range && (
                <span className="text-lg font-semibold text-emerald-600">{salon.price_range}</span>
              )}
              <button
                type="button"
                onClick={() => setEditing(true)}
                className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
              >
                Edit
              </button>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="inline-flex items-center gap-1 text-gray-500">
              <span aria-hidden>📍</span>
              {salon.district}
            </span>
            <RatingStars rating={salon.rating} reviewCount={salon.review_count} />
          </div>
          <ServiceTags services={salon.services} max={20} />
        </div>

        {salon.review_summary && (
          <div className="border-b border-gray-100 bg-rose-50/50 p-6">
            <p className="mb-2 inline-flex items-center gap-1.5 text-sm font-semibold text-rose-700">
              <span aria-hidden>✨</span> AI review summary
            </p>
            <p className="whitespace-pre-line text-sm leading-relaxed text-gray-700">
              {salon.review_summary}
            </p>
          </div>
        )}

        <dl className="grid grid-cols-1 gap-4 p-6 sm:grid-cols-2">
          <Field label="Address">
            <a className="text-rose-700 hover:underline" href={mapsHref} target="_blank" rel="noreferrer">
              {salon.address}
            </a>
          </Field>
          <Field label="Phone">
            {salon.phone ? (
              <a className="text-rose-700 hover:underline" href={`tel:${salon.phone}`}>
                {salon.phone}
              </a>
            ) : (
              <span className="text-gray-400">—</span>
            )}
          </Field>
          <Field label="Website">
            {salon.website ? (
              <a
                className="break-all text-rose-700 hover:underline"
                href={salon.website}
                target="_blank"
                rel="noreferrer"
              >
                {salon.website}
              </a>
            ) : (
              <span className="text-gray-400">—</span>
            )}
          </Field>
        </dl>
      </div>
    </DetailShell>
  );
}

function DetailShell({ children }: { children: React.ReactNode }) {
  return (
    <main className="mx-auto w-full max-w-3xl flex-1 px-6 py-8">
      <Link href="/" className="mb-6 inline-block text-sm text-gray-500 hover:text-rose-700">
        ← Back to all salons
      </Link>
      {children}
    </main>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase tracking-wide text-gray-400">{label}</dt>
      <dd className="mt-1 text-sm text-gray-700">{children}</dd>
    </div>
  );
}
