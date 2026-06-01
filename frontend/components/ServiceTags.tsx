import type { Service } from "@/lib/types";

/**
 * Renders service names as pills. Shows up to `max` tags and a "+N" overflow
 * indicator so cards stay compact.
 */
export function ServiceTags({ services, max = 4 }: { services: Service[]; max?: number }) {
  if (services.length === 0) return null;
  const shown = services.slice(0, max);
  const remaining = services.length - shown.length;

  return (
    <div className="flex flex-wrap gap-1.5">
      {shown.map((service) => (
        <span
          key={service.slug}
          className="rounded-full border border-line/70 bg-ink-3/50 px-2.5 py-0.5 text-xs text-ash"
        >
          {service.name}
        </span>
      ))}
      {remaining > 0 && (
        <span className="rounded-full border border-neon/30 px-2.5 py-0.5 text-xs font-medium text-neon-soft">
          +{remaining}
        </span>
      )}
    </div>
  );
}
