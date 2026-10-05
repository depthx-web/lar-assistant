import { AlertCircle, CheckCircle2, XCircle, Info } from "lucide-react";
import { cn } from "./cn";

type AlertVariant = "info" | "success" | "warning" | "error";

const variants: Record<AlertVariant, { icon: React.ReactNode; bg: string; border: string; text: string }> = {
  info: {
    icon: <Info className="h-4 w-4" />,
    bg: "bg-info-subtle",
    border: "border-info/20",
    text: "text-info",
  },
  success: {
    icon: <CheckCircle2 className="h-4 w-4" />,
    bg: "bg-success-subtle",
    border: "border-success/20",
    text: "text-success",
  },
  warning: {
    icon: <AlertCircle className="h-4 w-4" />,
    bg: "bg-warning-subtle",
    border: "border-warning/20",
    text: "text-warning",
  },
  error: {
    icon: <XCircle className="h-4 w-4" />,
    bg: "bg-error-subtle",
    border: "border-error/20",
    text: "text-error",
  },
};

interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export function Alert({ variant = "info", title, children, className }: AlertProps) {
  const v = variants[variant];
  return (
    <div className={cn("flex gap-3 p-4 rounded-lg border", v.bg, v.border, className)}>
      <span className={cn("shrink-0 mt-0.5", v.text)}>{v.icon}</span>
      <div>
        {title && <p className={cn("font-medium text-sm", v.text)}>{title}</p>}
        <p className="text-sm text-text-muted mt-0.5">{children}</p>
      </div>
    </div>
  );
}
