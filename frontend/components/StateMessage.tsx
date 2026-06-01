/** A centered status panel for loading / empty / error states. */
export function StateMessage({
  title,
  description,
  tone = "neutral",
}: {
  title: string;
  description?: string;
  tone?: "neutral" | "error";
}) {
  const titleColor = tone === "error" ? "text-neon-soft" : "text-porcelain";
  return (
    <div className="glass flex flex-col items-center justify-center gap-2 rounded-2xl px-6 py-16 text-center">
      <p className={`font-display text-lg ${titleColor}`}>{title}</p>
      {description && <p className="max-w-md text-sm text-ash">{description}</p>}
    </div>
  );
}
