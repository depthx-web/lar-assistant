import React from "react";
import { cn } from "./cn";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  size?: "sm" | "md" | "lg";
}

export function Modal({ open, onClose, title, description, children, footer, size = "md" }: ModalProps) {
  if (!open) return null;

  const sizes: Record<string, string> = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" role="dialog" aria-modal="true">
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className={cn("relative bg-surface border border-border rounded-xl shadow-xl w-full mx-4", sizes[size])}>
        <div className="flex items-start justify-between p-5 border-b border-border">
          <div>
            <h2 className="text-base font-semibold text-text">{title}</h2>
            {description && <p className="text-sm text-text-muted mt-0.5">{description}</p>}
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-text-faint hover:text-text hover:bg-surface-2 transition-colors ml-auto"
          >
            ✕
          </button>
        </div>
        <div className="p-5">{children}</div>
        {footer && (
          <div className="flex items-center justify-end gap-2 p-4 border-t border-border bg-surface-2/50 rounded-b-xl">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}