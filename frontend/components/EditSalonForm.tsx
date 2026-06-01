"use client";

import { useState } from "react";
import useSWR from "swr";

import { getDistricts, getServices, updateSalon } from "@/lib/api";
import type { SalonDetail, SalonUpdate } from "@/lib/types";

const PRICE_OPTIONS = ["", "$", "$$", "$$$"];
const inputClass =
  "w-full rounded-xl border border-line bg-ink-2/70 px-3.5 py-2.5 text-sm text-porcelain " +
  "[color-scheme:dark] transition placeholder:text-ash-dim focus:border-neon/60 " +
  "focus:outline-none focus:ring-2 focus:ring-neon/20";

/** Inline form to edit a salon and persist changes via `PATCH /salons/{id}`. */
export function EditSalonForm({
  salon,
  onSaved,
  onCancel,
}: {
  salon: SalonDetail;
  onSaved: (updated: SalonDetail) => void;
  onCancel: () => void;
}) {
  const { data: districts } = useSWR("districts", getDistricts);
  const { data: services } = useSWR("services", getServices);

  const [form, setForm] = useState({
    name: salon.name,
    address: salon.address,
    district: salon.district,
    phone: salon.phone ?? "",
    website: salon.website ?? "",
    price_range: salon.price_range ?? "",
    rating: salon.rating?.toString() ?? "",
  });
  const [selectedServices, setSelectedServices] = useState<Set<string>>(
    new Set(salon.services.map((s) => s.slug)),
  );
  const [saving, setSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  function update<K extends keyof typeof form>(key: K, value: string) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function toggleService(slug: string) {
    setSelectedServices((prev) => {
      const next = new Set(prev);
      if (next.has(slug)) next.delete(slug);
      else next.add(slug);
      return next;
    });
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true);
    setErrorMessage(null);

    const payload: SalonUpdate = {
      name: form.name,
      address: form.address,
      district: form.district,
      phone: form.phone || null,
      website: form.website || null,
      price_range: form.price_range || null,
      rating: form.rating === "" ? null : Number(form.rating),
      service_slugs: [...selectedServices],
    };

    try {
      const updated = await updateSalon(salon.id, payload);
      onSaved(updated);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to save changes");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rise glass flex flex-col gap-6 rounded-3xl p-7 sm:p-9"
    >
      <h2 className="font-display text-2xl font-light text-porcelain">Edit salon</h2>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <Labeled label="Name">
          <input
            className={inputClass}
            aria-label="Salon name"
            required
            value={form.name}
            onChange={(e) => update("name", e.target.value)}
          />
        </Labeled>
        <Labeled label="District">
          <select
            className={inputClass}
            value={form.district}
            onChange={(e) => update("district", e.target.value)}
          >
            {(districts ?? [salon.district]).map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </Labeled>
        <Labeled label="Address">
          <input
            className={inputClass}
            required
            value={form.address}
            onChange={(e) => update("address", e.target.value)}
          />
        </Labeled>
        <Labeled label="Phone">
          <input className={inputClass} value={form.phone} onChange={(e) => update("phone", e.target.value)} />
        </Labeled>
        <Labeled label="Website">
          <input className={inputClass} value={form.website} onChange={(e) => update("website", e.target.value)} />
        </Labeled>
        <Labeled label="Price range">
          <select
            className={inputClass}
            value={form.price_range}
            onChange={(e) => update("price_range", e.target.value)}
          >
            {PRICE_OPTIONS.map((p) => (
              <option key={p || "none"} value={p}>
                {p || "—"}
              </option>
            ))}
          </select>
        </Labeled>
        <Labeled label="Rating (0–5)">
          <input
            className={inputClass}
            type="number"
            min={0}
            max={5}
            step={0.1}
            value={form.rating}
            onChange={(e) => update("rating", e.target.value)}
          />
        </Labeled>
      </div>

      <fieldset>
        <legend className="mb-3 font-mono text-[10px] uppercase tracking-[0.2em] text-ash-dim">
          Services
        </legend>
        <div className="flex flex-wrap gap-2">
          {(services ?? salon.services).map((service) => {
            const checked = selectedServices.has(service.slug);
            return (
              <label
                key={service.slug}
                className={`cursor-pointer rounded-full border px-3 py-1.5 text-xs transition ${
                  checked
                    ? "border-neon/50 bg-neon/10 text-neon-soft"
                    : "border-line text-ash hover:border-line/60 hover:text-porcelain"
                }`}
              >
                <input
                  type="checkbox"
                  className="sr-only"
                  checked={checked}
                  onChange={() => toggleService(service.slug)}
                />
                {service.name}
              </label>
            );
          })}
        </div>
      </fieldset>

      {errorMessage && <p className="text-sm text-neon-soft">{errorMessage}</p>}

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={saving}
          className="rounded-xl bg-neon px-6 py-2.5 font-mono text-xs uppercase tracking-[0.15em] text-ink transition hover:bg-neon-soft hover:shadow-[0_0_24px_-4px_rgba(255,77,109,0.8)] disabled:opacity-50"
        >
          {saving ? "Saving…" : "Save changes"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="rounded-xl border border-line px-6 py-2.5 font-mono text-xs uppercase tracking-[0.15em] text-ash transition hover:text-porcelain"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}

function Labeled({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="flex flex-col gap-2">
      <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-ash-dim">{label}</span>
      {children}
    </label>
  );
}
