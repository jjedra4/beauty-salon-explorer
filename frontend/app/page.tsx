/**
 * Landing page (M0 placeholder).
 *
 * A minimal, on-brand page that confirms the frontend builds and serves. The
 * real listing/search UI replaces this in milestones M6–M7.
 */
export default function Home() {
  return (
    <main className="mx-auto flex max-w-2xl flex-1 flex-col items-center justify-center gap-6 px-6 py-24 text-center">
      <span className="rounded-full bg-pink-100 px-3 py-1 text-sm font-medium text-pink-700">
        Warsaw Accelerator 2026
      </span>
      <h1 className="text-balance text-4xl font-bold tracking-tight sm:text-5xl">
        Warsaw Beauty Salon Explorer
      </h1>
      <p className="text-balance text-lg text-gray-600">
        Browse, search, and discover hair &amp; beauty salons across Warsaw —
        powered by an AI-enriched dataset.
      </p>
      <p className="text-sm text-gray-400">
        Foundation scaffolding (M0) is live. The listing and search experience
        arrives in upcoming milestones.
      </p>
    </main>
  );
}
