import {
  Activity,
  BookOpen,
  FlaskConical,
  History,
  LayoutDashboard,
  ShieldAlert,
  type LucideIcon,
  TrendingUp,
} from "lucide-react";

export interface NavItem {
  href: string;
  label: string;
  shortLabel: string;
  icon: LucideIcon;
  /** Shown in the mobile bottom bar (max 5); the rest live in the footer on mobile. */
  primary: boolean;
}

export const NAV_ITEMS: NavItem[] = [
  {
    href: "/",
    label: "Market dashboard",
    shortLabel: "Markets",
    icon: LayoutDashboard,
    primary: true,
  },
  {
    href: "/predictions",
    label: "Forecasts",
    shortLabel: "Forecasts",
    icon: TrendingUp,
    primary: true,
  },
  {
    href: "/predictions/history",
    label: "Forecast history",
    shortLabel: "History",
    icon: History,
    primary: true,
  },
  {
    href: "/backtesting",
    label: "Evaluation",
    shortLabel: "Evaluation",
    icon: FlaskConical,
    primary: true,
  },
  { href: "/system", label: "System status", shortLabel: "System", icon: Activity, primary: true },
  {
    href: "/methodology",
    label: "Methodology",
    shortLabel: "Method",
    icon: BookOpen,
    primary: false,
  },
  {
    href: "/limitations",
    label: "Risks & limitations",
    shortLabel: "Risks",
    icon: ShieldAlert,
    primary: false,
  },
];

/** `/predictions` must not light up while on `/predictions/history`. */
export function isActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/" || pathname.startsWith("/markets/");
  if (pathname === href) return true;
  const deeper = NAV_ITEMS.some(
    (item) => item.href !== href && item.href.startsWith(href) && pathname.startsWith(item.href),
  );
  return !deeper && pathname.startsWith(`${href}/`);
}
