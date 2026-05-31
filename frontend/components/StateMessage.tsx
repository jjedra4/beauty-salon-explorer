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
  const titleColor = tone === "error" ? "text-red-600" : "text-gray-700";
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-2xl border border-dashed border-gray-200 px-6 py-16 text-center">
      <p className={`font-medium ${titleColor}`}>{title}</p>
      {description && <p className="max-w-md text-sm text-gray-500">{description}</p>}
    </div>
  );
}
