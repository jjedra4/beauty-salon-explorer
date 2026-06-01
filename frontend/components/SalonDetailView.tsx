"use client";

import Link from "next/link";
import { useState } from "react";
import useSWR from "swr";

import { EditSalonForm } from "@/components/EditSalonForm";
import { RatingStars } from "@/components/RatingStars";
import { ReviewSummary } from "@/components/ReviewSummary";
import { ServiceTags } from "@/components/ServiceTags";
import { StateMessage } from "@/components/StateMessage";
import { ApiError, getSalon } from "@/lib/api";

/** Salon detail view with an inline edit mode (persists via the API). */
export function SalonDetailView({ salonId }: { salonId: number }) {
  const [editing, setEditing] = useState(false);
  const {
    data: salon,
    error,
    isLoading,
    mutate,
  } = useSWR(Number.isFinite(salonId) ? ["salon", salonId] : null, () => getSalon(salonId));

  if (isLoading) {
    return (
      <DetailShell>
        <div className="shimmer h-96 rounded-3xl" />
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
      <article className="rise glass overflow-hidden rounded-3xl">
        <header className="relative flex flex-col gap-4 border-b border-line/50 p-7 sm:p-9">
          <span className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-neon/60 to-transparent" />
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="inline-flex items-center gap-1.5 font-mono text-xs uppercase tracking-[0.16em] text-ash">
                <span className="inline-block h-1.5 w-1.5 rounded-full bg-neon shadow-[0_0_6px_rgba(255,77,109,0.8)]" />
                {salon.district}
              </p>
              <h1 className="mt-3 font-display text-4xl font-light leading-tight text-porcelain sm:text-5xl">
                {salon.name}
              </h1>
            </div>
            <div className="flex items-center gap-4">
              {salon.price_range && (
                <span className="font-mono text-xl text-gold">{salon.price_range}</span>
              )}
              <button
                type="button"
                onClick={() => setEditing(true)}
                className="rounded-xl border border-line bg-ink-2/60 px-4 py-2 font-mono text-xs uppercase tracking-[0.14em] text-porcelain transition hover:border-neon/50 hover:text-neon-soft"
              >
                Edit
              </button>
            </div>
          </div>
          <div className="flex items-center gap-5">
            <RatingStars rating={salon.rating} reviewCount={salon.review_count} />
          </div>
          <ServiceTags services={salon.services} max={20} />
        </header>

        {salon.review_summary && <ReviewSummary text={salon.review_summary} />}

        <dl className="grid grid-cols-1 gap-6 p-7 sm:grid-cols-2 sm:p-9">
          <Field label="Address">
            <a className="text-neon-soft transition hover:text-neon" href={mapsHref} target="_blank" rel="noreferrer">
              {salon.address}
            </a>
          </Field>
          <Field label="Phone">
            {salon.phone ? (
              <a className="text-neon-soft transition hover:text-neon" href={`tel:${salon.phone}`}>
                {salon.phone}
              </a>
            ) : (
              <span className="text-ash-dim">—</span>
            )}
          </Field>
          <Field label="Website">
            {salon.website ? (
              <a
                className="break-all text-neon-soft transition hover:text-neon"
                href={salon.website}
                target="_blank"
                rel="noreferrer"
              >
                {salon.website}
              </a>
            ) : (
              <span className="text-ash-dim">—</span>
            )}
          </Field>
        </dl>
      </article>
    </DetailShell>
  );
}

function DetailShell({ children }: { children: React.ReactNode }) {
  return (
    <main className="mx-auto w-full max-w-3xl flex-1 px-6 py-10">
      <Link
        href="/browse"
        className="mb-7 inline-block font-mono text-[11px] uppercase tracking-[0.18em] text-ash transition-colors hover:text-neon-soft"
      >
        ← Back to directory
      </Link>
      {children}
    </main>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <dt className="font-mono text-[10px] uppercase tracking-[0.2em] text-ash-dim">{label}</dt>
      <dd className="mt-2 text-sm text-porcelain">{children}</dd>
    </div>
  );
}
