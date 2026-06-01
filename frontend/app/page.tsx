import { PromptSearch } from "@/components/PromptSearch";
import { TrendingStrip } from "@/components/TrendingStrip";

/**
 * Discover (home) — an AI-concierge hero. The oversized prompt bar is the
 * centre of gravity; a small "trending" strip hints at the catalogue without
 * crowding it. Submitting routes to the dedicated `/search` results page.
 */
export default function Home() {
  return (
    <main className="relative flex-1">
      <section className="mx-auto flex max-w-3xl flex-col items-center px-6 pb-16 pt-20 text-center sm:pt-28">
        <p
          className="rise font-mono text-[11px] uppercase tracking-[0.34em] text-ash"
          style={{ animationDelay: "0ms" }}
        >
          Warsaw · Hair &amp; Beauty · AI Concierge
        </p>

        <h1
          className="rise mt-7 font-display text-5xl font-light leading-[1.02] text-porcelain sm:text-7xl"
          style={{ animationDelay: "90ms" }}
        >
          Describe the salon.
          <br />
          The <span className="neon-text italic">atelier</span> finds it.
        </h1>

        <p
          className="rise mt-6 max-w-xl text-balance text-base leading-relaxed text-ash sm:text-lg"
          style={{ animationDelay: "180ms" }}
        >
          No dropdowns, no guesswork. Ask in plain Polish or English — a late-night
          barber, a balayage specialist, a calm spa near the Old Town — and vector
          search ranks the matches.
        </p>

        <div className="rise mt-11 w-full" style={{ animationDelay: "280ms" }}>
          <PromptSearch size="hero" />
        </div>
      </section>

      <TrendingStrip />
    </main>
  );
}
