import { Suspense } from "react";

import { PromptSearch } from "@/components/PromptSearch";
import { SalonBrowser } from "@/components/SalonBrowser";
import { StateMessage } from "@/components/StateMessage";

/**
 * Directory (browse) route. A lightweight server shell wraps the client-side
 * `SalonBrowser` in a `<Suspense>` boundary (required because it reads
 * `useSearchParams`).
 */
export default function BrowsePage() {
  return (
    <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-10">
      <div className="rise mb-8">
        <p className="font-mono text-[11px] uppercase tracking-[0.3em] text-ash">The directory</p>
        <h1 className="mt-3 font-display text-4xl font-light text-porcelain sm:text-5xl">
          Browse every salon
        </h1>
        <p className="mt-3 max-w-xl text-ash">
          Filter by district or service. Looking for something specific?{" "}
          <span className="text-porcelain">Just ask</span> —
        </p>
      </div>

      <div className="rise mb-10" style={{ animationDelay: "80ms" }}>
        <PromptSearch size="compact" />
      </div>

      <Suspense fallback={<StateMessage title="Loading…" />}>
        <SalonBrowser />
      </Suspense>
    </main>
  );
}
