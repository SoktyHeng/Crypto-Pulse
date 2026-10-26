import Link from "next/link";
import { Activity } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { EXCHANGE } from "@/lib/markets";
import { MobileNav } from "./mobile-nav";
import { NAV_ITEMS } from "./nav-items";
import { SidebarNav } from "./sidebar-nav";
import { ThemeToggle } from "./theme-toggle";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-dvh md:grid md:grid-cols-[15rem_1fr]">
      <a
        href="#main"
        className="sr-only z-50 rounded-md bg-primary px-3 py-2 text-primary-foreground focus:not-sr-only focus:fixed focus:top-2 focus:left-2"
      >
        Skip to content
      </a>

      <aside className="hidden border-r bg-sidebar md:sticky md:top-0 md:flex md:h-dvh md:flex-col">
        <div className="flex h-14 items-center gap-2 border-b px-5">
          <Activity className="size-5 text-primary" aria-hidden="true" />
          <span className="font-semibold tracking-tight">CryptoPulse AI</span>
        </div>
        <SidebarNav />
      </aside>

      <div className="flex min-w-0 flex-col">
        <header className="sticky top-0 z-30 flex h-14 items-center justify-between gap-3 border-b bg-background/95 px-4 backdrop-blur md:px-6">
          <Link href="/" className="flex items-center gap-2 font-semibold tracking-tight md:hidden">
            <Activity className="size-5 text-primary" aria-hidden="true" />
            CryptoPulse AI
          </Link>
          <div className="hidden items-center gap-2 text-sm text-muted-foreground md:flex">
            <span>Source:</span>
            <Badge variant="outline">{EXCHANGE.label}</Badge>
            <span>· USDT spot markets · times shown in your local timezone</span>
          </div>
          <ThemeToggle />
        </header>

        <main id="main" className="flex-1 px-4 py-6 pb-24 md:px-6 md:pb-8">
          {children}
        </main>

        <footer className="border-t px-4 py-4 pb-20 text-xs text-muted-foreground md:px-6 md:pb-4">
          <p>
            Informational analysis only — not financial advice. Forecasts are statistical and
            uncertain; markets can move against any forecast.
          </p>
          <nav aria-label="Footer" className="mt-2 flex flex-wrap gap-x-4 gap-y-1">
            {NAV_ITEMS.filter((item) => !item.primary).map((item) => (
              <Link key={item.href} href={item.href} className="underline-offset-4 hover:underline">
                {item.label}
              </Link>
            ))}
          </nav>
        </footer>
      </div>

      <MobileNav />
    </div>
  );
}
