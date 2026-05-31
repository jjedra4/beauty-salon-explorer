import { Suspense } from "react";

import { SalonBrowser } from "@/components/SalonBrowser";
import { StateMessage } from "@/components/StateMessage";

/**
 * Listing page. A lightweight server shell wraps the client-side
 * `SalonBrowser` in a `<Suspense>` boundary (required because the browser
 * reads `useSearchParams`).
 */
export default function Home() {
  return (
    <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">
          Browse Warsaw salons
        </h1>
        <p className="mt-1 text-gray-500">
          Filter by district or service to find your next hair &amp; beauty spot.
        </p>
      </div>

      <Suspense fallback={<StateMessage title="Loading…" />}>
        <SalonBrowser />
      </Suspense>
    </main>
  );
}
