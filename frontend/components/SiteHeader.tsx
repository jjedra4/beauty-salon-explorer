import Link from "next/link";

/** App header with the brand, shown on every page. */
export function SiteHeader() {
  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-xl" aria-hidden>
            💇
          </span>
          <span className="font-semibold text-gray-900">Warsaw Salon Explorer</span>
        </Link>
        <span className="hidden text-sm text-gray-400 sm:block">
          Find hair &amp; beauty salons across Warsaw
        </span>
      </div>
    </header>
  );
}
