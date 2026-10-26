import type { Metadata, Viewport } from "next";
import { AppShell } from "@/components/layout/app-shell";
import { Providers } from "@/components/providers";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "CryptoPulse AI", template: "%s · CryptoPulse AI" },
  description:
    "Transparent short-horizon trend analysis for Binance Spot BTC, ETH and SOL USDT markets. Informational only; not financial advice.",
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#fafafa" },
    { media: "(prefers-color-scheme: dark)", color: "#16171c" },
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Providers>
          <AppShell>{children}</AppShell>
        </Providers>
      </body>
    </html>
  );
}
