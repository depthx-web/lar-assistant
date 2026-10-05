import React, { useState, useCallback, useContext } from "react";

type ToastVariant = "success" | "error" | "warning" | "info";

interface ToastData {
  id: string;
  variant: ToastVariant;
  title: string;
  description?: string;
}

const ToastContext = React.createContext<{ toasts: ToastData[]; addToast: (data: Omit<ToastData, "id">) => void; removeToast: (id: string) => void } | null>(null);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastData[]>([]);
  const addToast = useCallback((data: Omit<ToastData, "id">) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((prev) => [...prev, { ...data, id }]);
    setTimeout(() => removeToast(id), 4000);
  }, []);
  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);
  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <ToastContainer />
    </ToastContext.Provider>
  );
}

function ToastContainer() {
  const { toasts } = useContext(ToastContext)!;
  if (toasts.length === 0) return null;
  return (
    <>
      {toasts.map((toast) => (
        <div key={toast.id} className="toast">
          {toast.title}{toast.description ? <span> – {toast.description}</span> : null}
        </div>
      ))}
    </>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}