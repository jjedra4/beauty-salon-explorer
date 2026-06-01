import type { SearchMode } from "@/lib/types";

/**
 * Signals which retrieval path produced the results: AI vector search
 * (semantic) or the keyword/trigram fallback used when no AI key is configured.
 */
export function ModeBadge({ mode }: { mode: SearchMode }) {
  const semantic = mode === "semantic";
  return (
    <span
      title={
        semantic
          ? "AI semantic search — vector similarity over salon embeddings + LLM-extracted filters"
          : "Keyword fallback — trigram matching (no AI key configured)"
      }
      className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 font-mono text-[10px] uppercase tracking-[0.18em] ${
        semantic
          ? "border border-neon/40 text-neon-soft neon-ring"
          : "border border-line text-ash"
      }`}
    >
      <span aria-hidden>{semantic ? "✦" : "#"}</span>
      {semantic ? "Semantic" : "Keyword"}
    </span>
  );
}
