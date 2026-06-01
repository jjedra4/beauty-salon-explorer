import { Suspense } from "react";

import { SearchView } from "@/components/SearchView";
import { StateMessage } from "@/components/StateMessage";

/**
 * Search results route. A thin server shell wraps the client `SearchView` in a
 * `<Suspense>` boundary (required because the view reads `useSearchParams`).
 */
export default function SearchPage() {
  return (
    <Suspense
      fallback={
        <main className="mx-auto w-full max-w-5xl flex-1 px-6 py-10">
          <StateMessage title="Loading…" />
        </main>
      }
    >
      <SearchView />
    </Suspense>
  );
}
