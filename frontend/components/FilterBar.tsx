import type { Service } from "@/lib/types";

/** Controlled district + service dropdowns. Empty value means "no filter". */
export function FilterBar({
  districts,
  services,
  district,
  service,
  onDistrictChange,
  onServiceChange,
}: {
  districts: string[];
  services: Service[];
  district: string;
  service: string;
  onDistrictChange: (value: string) => void;
  onServiceChange: (value: string) => void;
}) {
  const selectClass =
    "rounded-xl border border-line bg-ink-2/70 px-3.5 py-2 text-sm text-porcelain " +
    "[color-scheme:dark] transition focus:border-neon/60 focus:outline-none " +
    "focus:ring-2 focus:ring-neon/20 hover:border-line/60";
  const labelClass =
    "flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.16em] text-ash-dim";

  return (
    <div className="flex flex-wrap items-center gap-4">
      <label className={labelClass}>
        District
        <select
          aria-label="Filter by district"
          className={selectClass}
          value={district}
          onChange={(event) => onDistrictChange(event.target.value)}
        >
          <option value="">All districts</option>
          {districts.map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>
      </label>

      <label className={labelClass}>
        Service
        <select
          aria-label="Filter by service"
          className={selectClass}
          value={service}
          onChange={(event) => onServiceChange(event.target.value)}
        >
          <option value="">All services</option>
          {services.map((item) => (
            <option key={item.slug} value={item.slug}>
              {item.name}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
