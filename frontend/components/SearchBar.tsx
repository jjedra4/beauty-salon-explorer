"use client";

import { useState } from "react";

/**
 * Natural-language search input. Presentational: the parent owns the query
 * state (kept in the URL) and reacts to `onSearch` / `onClear`.
 */
export function SearchBar({
  initialQuery,
  onSearch,
  onClear,
}: {
  initialQuery: string;
  onSearch: (query: string) => void;
  onClear: () => void;
}) {
  const [value, setValue] = useState(initialQuery);

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    onSearch(value.trim());
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2" role="search">
      <input
        type="search"
        aria-label="Search salons"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="Try: cheap barber in Mokotów with great reviews"
        className="w-full rounded-xl border border-gray-300 bg-white px-4 py-2.5 text-gray-900 placeholder:text-gray-400 focus:border-rose-400 focus:outline-none focus:ring-2 focus:ring-rose-100"
      />
      <button
        type="submit"
        className="shrink-0 rounded-xl bg-rose-600 px-5 py-2.5 font-medium text-white transition hover:bg-rose-700"
      >
        Search
      </button>
      {initialQuery && (
        <button
          type="button"
          onClick={() => {
            setValue("");
            onClear();
          }}
          className="shrink-0 rounded-xl border border-gray-300 px-4 py-2.5 font-medium text-gray-600 transition hover:bg-gray-50"
        >
          Clear
        </button>
      )}
    </form>
  );
}
