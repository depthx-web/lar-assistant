import type { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger" | "ok" | "bad";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
}

export function Button({
  variant = "secondary",
  size = "md",
  loading = false,
  disabled,
  className,
  children,
  ...props
}: ButtonProps) {
  const classes: Record<string, string> = {
    primary: "pri",
    secondary: "",
    ghost: "ghost",
    danger: "bad",
    ok: "ok",
    bad: "bad",
  };
  const cls = classes[variant] || "";
  const sizeCls = size === "sm" ? "sm" : "";
  const combined = ["btn", cls, sizeCls, className].filter(Boolean).join(" ");

  return (
    <button className={combined} disabled={disabled || loading} {...props}>
      {children}
    </button>
  );
}
