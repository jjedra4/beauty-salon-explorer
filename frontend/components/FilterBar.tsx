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
    "rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 " +
    "focus:border-rose-400 focus:outline-none focus:ring-2 focus:ring-rose-100";

  return (
    <div className="flex flex-wrap items-center gap-3">
      <label className="flex items-center gap-2 text-sm text-gray-500">
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

      <label className="flex items-center gap-2 text-sm text-gray-500">
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
