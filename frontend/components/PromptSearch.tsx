"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { useTypewriter } from "@/lib/useTypewriter";

/** Example queries that "write themselves" in the bar and seed the quick chips. */
export const EXAMPLE_PROMPTS = [
  "tani fryzjer na Mokotowie z dobrymi opiniami",
  "balayage specialist open late in Śródmieście",
  "calm spa for a facial near the Old Town",
  "barber for a skin fade, walk-ins welcome",
  "gdzie zrobię paznokcie hybrydowe w Pradze?",
];

/**
 * The hero search — an oversized "concierge" prompt bar. While empty and idle,
 * ghosted example prompts type themselves out behind the cursor; on submit it
 * routes to the dedicated `/search` results page.
 */
export function PromptSearch({ size = "hero" }: { size?: "hero" | "compact" }) {
  const router = useRouter();
  const [value, setValue] = useState("");
  const [focused, setFocused] = useState(false);

  const idle = value === "" && !focused;
  const ghost = useTypewriter(EXAMPLE_PROMPTS, { enabled: idle });

  function run(query: string) {
    const q = query.trim();
    if (q) router.push(`/search?q=${encodeURIComponent(q)}`);
  }

  const hero = size === "hero";

  return (
    <div className="w-full">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          run(value);
        }}
        role="search"
        className={`group glass relative flex items-center gap-3 rounded-2xl transition-shadow duration-300 ${
          hero ? "px-5 py-4 sm:gap-4 sm:px-7 sm:py-6" : "px-4 py-3"
        } ${focused ? "neon-ring" : "hover:shadow-[0_0_40px_-16px_rgba(255,77,109,0.5)]"}`}
      >
        <SparkIcon className={hero ? "h-7 w-7" : "h-5 w-5"} />

        <div className="relative flex-1">
          {/* Ghost prompt that types itself — hidden once the user engages. */}
          {idle && (
            <div
              aria-hidden
              className={`pointer-events-none absolute inset-0 flex items-center font-mono text-ash-dim ${
                hero ? "text-base sm:text-lg" : "text-sm"
              }`}
            >
              <span className="caret truncate opacity-70">{ghost}</span>
            </div>
          )}
          <input
            type="search"
            aria-label="Describe the salon you're looking for"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            className={`w-full bg-transparent font-sans text-porcelain caret-neon placeholder:text-transparent focus:outline-none ${
              hero ? "text-base sm:text-lg" : "text-sm"
            }`}
          />
        </div>

        <button
          type="submit"
          className={`shrink-0 rounded-xl bg-neon font-mono uppercase tracking-[0.15em] text-ink transition hover:bg-neon-soft hover:shadow-[0_0_24px_-4px_rgba(255,77,109,0.8)] active:scale-95 ${
            hero ? "px-5 py-3 text-xs sm:px-7 sm:text-sm" : "px-4 py-2 text-[11px]"
          }`}
        >
          Ask
        </button>
      </form>

      {hero && (
        <div className="mt-5 flex flex-wrap items-center gap-2">
          <span className="font-mono text-[11px] uppercase tracking-[0.22em] text-ash-dim">
            Try
          </span>
          {EXAMPLE_PROMPTS.slice(0, 3).map((prompt) => (
            <button
              key={prompt}
              type="button"
              onClick={() => run(prompt)}
              className="rounded-full border border-line/80 bg-ink-2/50 px-3 py-1.5 text-xs text-ash transition hover:border-neon/50 hover:text-porcelain"
            >
              {prompt}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function SparkIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden
      className={`shrink-0 text-neon drop-shadow-[0_0_8px_rgba(255,77,109,0.6)] ${className ?? ""}`}
    >
      <path
        d="M12 2.5c.6 4.7 2.3 6.4 7 7-4.7.6-6.4 2.3-7 7-.6-4.7-2.3-6.4-7-7 4.7-.6 6.4-2.3 7-7Z"
        fill="currentColor"
      />
    </svg>
  );
}
