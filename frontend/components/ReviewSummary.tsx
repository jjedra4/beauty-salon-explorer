import { parseReviewSummary } from "@/lib/reviewSummary";

/**
 * The AI review summary block on the detail page: a one-line vibe, then pros and
 * cons side by side, colour-coded (mint for pros, rose for cons) so they read at
 * a glance. Falls back to plain prose when the summary has no clear structure.
 */
export function ReviewSummary({ text }: { text: string }) {
  const { vibe, pros, cons } = parseReviewSummary(text);
  const hasColumns = pros.length > 0 || cons.length > 0;

  return (
    <section className="border-b border-line/50 bg-neon/[0.04] p-7 sm:p-9">
      <p className="mb-4 inline-flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.2em] text-neon-soft">
        <span aria-hidden>✦</span> AI review summary
      </p>

      {vibe && (
        <p className="mb-5 font-display text-lg leading-relaxed text-porcelain/90">{vibe}</p>
      )}

      {hasColumns && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <ProsConsCard tone="pros" items={pros} />
          <ProsConsCard tone="cons" items={cons} />
        </div>
      )}
    </section>
  );
}

const TONES = {
  pros: {
    label: "Loved",
    glyph: "＋",
    ring: "border-mint/30 bg-mint/[0.05]",
    accent: "text-mint",
    marker: "bg-mint shadow-[0_0_6px_rgba(116,227,194,0.7)]",
    empty: "No standout positives mentioned.",
  },
  cons: {
    label: "Watch-outs",
    glyph: "－",
    ring: "border-neon/30 bg-neon/[0.05]",
    accent: "text-neon-soft",
    marker: "bg-neon shadow-[0_0_6px_rgba(255,77,109,0.7)]",
    empty: "No notable complaints mentioned.",
  },
} as const;

function ProsConsCard({ tone, items }: { tone: keyof typeof TONES; items: string[] }) {
  const t = TONES[tone];
  return (
    <div className={`rounded-2xl border p-5 ${t.ring}`}>
      <p
        className={`mb-3 inline-flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.18em] ${t.accent}`}
      >
        <span aria-hidden className="text-sm leading-none">
          {t.glyph}
        </span>
        {t.label}
      </p>
      {items.length === 0 ? (
        <p className="text-sm text-ash-dim">{t.empty}</p>
      ) : (
        <ul className="flex flex-col gap-2">
          {items.map((item, i) => (
            <li key={i} className="flex gap-2.5 text-sm leading-snug text-porcelain/85">
              <span aria-hidden className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${t.marker}`} />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
