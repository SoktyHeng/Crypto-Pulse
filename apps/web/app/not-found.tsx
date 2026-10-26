import Link from "next/link";
import { EmptyState } from "@/components/states/states";

export default function NotFound() {
  return (
    <EmptyState
      title="Page or market not found"
      description="Only BTCUSDT, ETHUSDT and SOLUSDT on Binance Spot are supported."
      code="NOT_FOUND"
    >
      <Link
        href="/"
        className="text-sm font-medium text-primary underline-offset-4 hover:underline"
      >
        Back to market dashboard
      </Link>
    </EmptyState>
  );
}
