import Link from "next/link";

/** App header: a neon wordmark and minimal nav, shown on every page. */
export function SiteHeader() {
  return (
    <header className="sticky top-0 z-30 border-b border-line/60 bg-ink/70 backdrop-blur-xl">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="group flex items-baseline gap-2.5">
          <span className="neon-text neon-pulse font-display text-2xl font-light italic leading-none">
            Salon
          </span>
          <span className="font-display text-2xl font-light leading-none text-porcelain">
            Atelier
          </span>
          <span className="ml-1 hidden font-mono text-[10px] uppercase tracking-[0.3em] text-ash-dim sm:inline">
            Warszawa
          </span>
        </Link>

        <nav className="flex items-center gap-1 font-mono text-xs uppercase tracking-[0.18em]">
          <NavLink href="/">Discover</NavLink>
          <NavLink href="/browse">Directory</NavLink>
        </nav>
      </div>
      <div className="hairline h-px w-full opacity-50" />
    </header>
  );
}

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      className="rounded-full px-3 py-1.5 text-ash transition-colors hover:bg-ink-3/60 hover:text-porcelain"
    >
      {children}
    </Link>
  );
}
