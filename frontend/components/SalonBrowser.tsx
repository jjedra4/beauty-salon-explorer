"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import useSWR from "swr";

import { FilterBar } from "@/components/FilterBar";
import { Pagination } from "@/components/Pagination";
import { SalonCard } from "@/components/SalonCard";
import { SearchBar } from "@/components/SearchBar";
import { StateMessage } from "@/components/StateMessage";
import { getDistricts, getServices, listSalons, searchSalons } from "@/lib/api";

const PAGE_SIZE = 12;

/**
 * Listing experience with two modes, both driven by the URL (shareable, back
 * button works) and fetched client-side with SWR:
 *
 * - **Browse** (default): district/service filters + pagination over `/salons`.
 * - **Search** (when `?q=` is set): natural-language results from
 *   `/salons/search`, with a badge showing whether semantic or keyword
 *   retrieval was used.
 *
 * Reads `useSearchParams`, so it must render inside a `<Suspense>` boundary.
 */
export function SalonBrowser() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const query = (searchParams.get("q") ?? "").trim();
  const district = searchParams.get("district") ?? "";
  const service = searchParams.get("service") ?? "";
  const offset = Number(searchParams.get("offset") ?? "0");
  const searching = query.length > 0;

  const { data: districts } = useSWR("districts", getDistricts);
  const { data: services } = useSWR("services", getServices);

  const list = useSWR(
    searching ? null : ["salons", district, service, offset],
    () =>
      listSalons({
        district: district || undefined,
        service: service || undefined,
        limit: PAGE_SIZE,
        offset,
      }),
    { keepPreviousData: true },
  );

  const search = useSWR(searching ? ["search", query] : null, () => searchSalons(query));

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
      <SearchBar
        initialQuery={query}
        // Searching clears the filters/pagination — search is its own mode.
        onSearch={(value) =>
          setParams({ q: value || null, district: null, service: null, offset: null })
        }
        onClear={() => setParams({ q: null })}
      />

      {searching ? (
        <SearchResults
          query={query}
          state={search}
        />
      ) : (
        <>
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
        </>
      )}
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
  if (state.isLoading && !state.data) return <StateMessage title="Loading salons…" />;
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
        {state.data.items.map((salon) => (
          <SalonCard key={salon.id} salon={salon} />
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

function SearchResults({
  query,
  state,
}: {
  query: string;
  state: SwrState<Awaited<ReturnType<typeof searchSalons>>>;
}) {
  if (state.error) {
    return <StateMessage tone="error" title="Search failed" description="Please try again." />;
  }
  if (state.isLoading && !state.data) return <StateMessage title="Searching…" />;
  if (!state.data) return null;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center gap-2 text-sm text-gray-500">
        <span>
          {state.data.items.length} result{state.data.items.length === 1 ? "" : "s"} for{" "}
          <span className="font-medium text-gray-700">“{query}”</span>
        </span>
        <ModeBadge mode={state.data.mode} />
      </div>

      {state.data.items.length === 0 ? (
        <StateMessage title="No matches" description="Try rephrasing your search." />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {state.data.items.map((salon) => (
            <SalonCard key={salon.id} salon={salon} />
          ))}
        </div>
      )}
    </div>
  );
}

function ModeBadge({ mode }: { mode: "semantic" | "keyword" }) {
  const semantic = mode === "semantic";
  return (
    <span
      title={
        semantic
          ? "AI semantic search (vector similarity + extracted filters)"
          : "Keyword fallback (no AI key configured)"
      }
      className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
        semantic ? "bg-rose-100 text-rose-700" : "bg-gray-100 text-gray-600"
      }`}
    >
      {semantic ? "✨ Semantic" : "Keyword"}
    </span>
  );
}
