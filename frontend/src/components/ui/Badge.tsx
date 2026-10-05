import { cn } from "./cn";
export function Badge({
  children,
  variant = "default",
  className,
}: {
  children: React.ReactNode;
  variant?: "default" | "success" | "warning" | "error" | "info" | "muted" | "official";
  className?: string;
}) {
  const classes: Record<string, string> = {
    default: "b-info",
    success: "b-ok",
    warning: "b-warn",
    error: "b-crit",
    info: "b-info",
    muted: "b-mute",
    official: "b-official",
  };

  return (
    <span className={cn("badge", classes[variant], className)}>
      {children}
    </span>
  );
}
