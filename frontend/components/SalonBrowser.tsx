"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import useSWR from "swr";

import { FilterBar } from "@/components/FilterBar";
import { Pagination } from "@/components/Pagination";
import { SalonCard } from "@/components/SalonCard";
import { StateMessage } from "@/components/StateMessage";
import { getDistricts, getServices, listSalons } from "@/lib/api";

const PAGE_SIZE = 12;

/**
 * The directory browser: district/service filters + pagination over `/salons`,
 * all driven by the URL (shareable, back button works) and fetched client-side
 * with SWR. Natural-language search lives on its own `/search` route.
 *
 * Reads `useSearchParams`, so it must render inside a `<Suspense>` boundary.
 */
export function SalonBrowser() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const district = searchParams.get("district") ?? "";
  const service = searchParams.get("service") ?? "";
  const offset = Number(searchParams.get("offset") ?? "0");

  const { data: districts } = useSWR("districts", getDistricts);
  const { data: services } = useSWR("services", getServices);

  const list = useSWR(
    ["salons", district, service, offset],
    () =>
      listSalons({
        district: district || undefined,
        service: service || undefined,
        limit: PAGE_SIZE,
        offset,
      }),
    { keepPreviousData: true },
  );

  /** Merge URL param updates and navigate. */
  function setParams(updates: Record<string, string | null>) {
    const params = new URLSearchParams(searchParams.toString());
    for (const [key, value] of Object.entries(updates)) {
      if (value) params.set(key, value);
      else params.delete(key);
    }
    router.push(params.toString() ? `${pathname}?${params}` : pathname);
  }

  return (
    <div className="flex flex-col gap-6">
      <FilterBar
        districts={districts ?? []}
        services={services ?? []}
        district={district}
        service={service}
        onDistrictChange={(value) => setParams({ district: value || null, offset: null })}
        onServiceChange={(value) => setParams({ service: value || null, offset: null })}
      />
      <BrowseResults
        state={list}
        onPageChange={(next) => setParams({ offset: next ? String(next) : null })}
      />
    </div>
  );
}

type SwrState<T> = { data?: T; error?: unknown; isLoading: boolean };

function BrowseResults({
  state,
  onPageChange,
}: {
  state: SwrState<Awaited<ReturnType<typeof listSalons>>>;
  onPageChange: (offset: number) => void;
}) {
  if (state.error) {
    return (
      <StateMessage
        tone="error"
        title="Couldn't load salons"
        description="Make sure the backend is running, then try again."
      />
    );
  }
  if (state.isLoading && !state.data) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="shimmer h-44 rounded-2xl" />
        ))}
      </div>
    );
  }
  if (!state.data) return null;
  if (state.data.items.length === 0) {
    return (
      <StateMessage
        title="No salons match these filters"
        description="Try clearing a filter to see more results."
      />
    );
  }
  return (
    <>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {state.data.items.map((salon, i) => (
          <div key={salon.id} className="rise" style={{ animationDelay: `${i * 45}ms` }}>
            <SalonCard salon={salon} />
          </div>
        ))}
      </div>
      <Pagination
        total={state.data.total}
        limit={state.data.limit}
        offset={state.data.offset}
        onChange={onPageChange}
      />
    </>
  );
}
