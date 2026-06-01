/** Quiet footer with the AI-pipeline credit line. */
export function SiteFooter() {
  return (
    <footer className="mt-auto border-t border-line/50 px-6 py-8">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 text-center sm:flex-row sm:text-left">
        <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-ash-dim">
          Salon Atelier · Warsaw
        </p>
        <p className="max-w-md text-xs leading-relaxed text-ash-dim">
          Listings curated by an AI data pipeline — normalised, de-duplicated and
          summarised. Search runs on vector embeddings with a keyword fallback.
        </p>
      </div>
    </footer>
  );
}
