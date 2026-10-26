"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { NAV_ITEMS, isActive } from "./nav-items";

export function MobileNav() {
  const pathname = usePathname();
  return (
    <nav
      aria-label="Main mobile"
      className="fixed inset-x-0 bottom-0 z-40 border-t bg-background/95 backdrop-blur md:hidden"
    >
      <ul className="grid grid-cols-5">
        {NAV_ITEMS.filter((item) => item.primary).map(({ href, shortLabel, icon: Icon }) => {
          const active = isActive(pathname, href);
          return (
            <li key={href}>
              <Link
                href={href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "flex min-h-14 flex-col items-center justify-center gap-0.5 text-[11px] text-muted-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none",
                  active && "font-medium text-foreground",
                )}
              >
                <Icon className="size-5" aria-hidden="true" />
                {shortLabel}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
