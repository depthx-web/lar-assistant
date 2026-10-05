import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import React, { useState, useCallback, useContext } from "react";
const ToastContext = React.createContext(null);
export function ToastProvider({ children }) {
    const [toasts, setToasts] = useState([]);
    const addToast = useCallback((data) => {
        const id = Math.random().toString(36).slice(2);
        setToasts((prev) => [...prev, { ...data, id }]);
        setTimeout(() => removeToast(id), 4000);
    }, []);
    const removeToast = useCallback((id) => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
    }, []);
    return (_jsxs(ToastContext.Provider, { value: { toasts, addToast, removeToast }, children: [children, _jsx(ToastContainer, {})] }));
}
function ToastContainer() {
    const { toasts } = useContext(ToastContext);
    if (toasts.length === 0)
        return null;
    return (_jsx(_Fragment, { children: toasts.map((toast) => (_jsxs("div", { className: "toast", children: [toast.title, toast.description ? _jsxs("span", { children: [" \u2013 ", toast.description] }) : null] }, toast.id))) }));
}
export function useToast() {
    const ctx = useContext(ToastContext);
    if (!ctx)
        throw new Error("useToast must be used within ToastProvider");
    return ctx;
}
