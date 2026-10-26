import { AlertTriangle, Inbox, RefreshCw, WifiOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

/**
 * First-class data states. None of these ever render placeholder numbers: loading uses
 * skeletons, and empty/error/offline explain what is missing and why.
 */

export function LoadingState({
  label,
  rows = 3,
  className,
}: {
  label: string;
  rows?: number;
  className?: string;
}) {
  return (
    <div role="status" aria-live="polite" className={cn("space-y-2", className)}>
      <span className="sr-only">{label}</span>
      {Array.from({ length: rows }, (_, i) => (
        <Skeleton key={i} className="h-5 w-full" />
      ))}
    </div>
  );
}

interface MessageStateProps {
  title: string;
  description: string;
  code?: string;
  className?: string;
  children?: React.ReactNode;
}

function MessageState({
  icon: Icon,
  title,
  description,
  code,
  className,
  children,
  tone,
}: MessageStateProps & { icon: typeof Inbox; tone: "muted" | "warning" | "danger" }) {
  return (
    <div
      className={cn(
        "flex flex-col items-start gap-2 rounded-lg border border-dashed p-4 text-sm",
        tone === "warning" && "border-warning/50",
        tone === "danger" && "border-loss/50",
        className,
      )}
    >
      <div className="flex items-center gap-2 font-medium">
        <Icon
          className={cn(
            "size-4",
            tone === "warning" && "text-warning",
            tone === "danger" && "text-loss",
          )}
          aria-hidden="true"
        />
        {title}
      </div>
      <p className="text-muted-foreground">{description}</p>
      {code ? (
        <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-xs">{code}</code>
      ) : null}
      {children}
    </div>
  );
}

export function EmptyState(props: MessageStateProps) {
  return <MessageState icon={Inbox} tone="muted" {...props} />;
}

export function ErrorState({ onRetry, ...props }: MessageStateProps & { onRetry?: () => void }) {
  return (
    <div role="alert">
      <MessageState icon={AlertTriangle} tone="danger" {...props}>
        {onRetry ? <RetryButton onRetry={onRetry} /> : null}
      </MessageState>
    </div>
  );
}

export function OfflineState({ onRetry, ...props }: MessageStateProps & { onRetry?: () => void }) {
  return (
    <div role="alert">
      <MessageState icon={WifiOff} tone="warning" {...props}>
        {onRetry ? <RetryButton onRetry={onRetry} /> : null}
      </MessageState>
    </div>
  );
}

function RetryButton({ onRetry }: { onRetry: () => void }) {
  return (
    <Button variant="outline" size="sm" onClick={onRetry}>
      <RefreshCw aria-hidden="true" />
      Retry
    </Button>
  );
}
