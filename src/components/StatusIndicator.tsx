import { cn } from "@/lib/utils";

type Status = "active" | "expiring" | "expired" | "trial";

const statusConfig: Record<Status, { label: string; dotClass: string; textClass: string }> = {
  active: { label: "Активна", dotClass: "bg-success", textClass: "text-success" },
  expiring: { label: "Истекает", dotClass: "bg-warning", textClass: "text-warning" },
  expired: { label: "Истекла", dotClass: "bg-destructive", textClass: "text-destructive" },
  trial: { label: "Пробная", dotClass: "bg-primary", textClass: "text-primary" },
};

export function StatusIndicator({ status, className }: { status: Status; className?: string }) {
  const config = statusConfig[status];
  return (
    <div className={cn("flex items-center gap-2", className)}>
      <span className={cn("h-2.5 w-2.5 rounded-full animate-pulse", config.dotClass)} />
      <span className={cn("text-sm font-medium", config.textClass)}>{config.label}</span>
    </div>
  );
}
