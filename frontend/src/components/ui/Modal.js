import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { cn } from "./cn";
export function Modal({ open, onClose, title, description, children, footer, size = "md" }) {
    if (!open)
        return null;
    const sizes = {
        sm: "max-w-sm",
        md: "max-w-md",
        lg: "max-w-lg",
    };
    return (_jsxs("div", { className: "fixed inset-0 z-50 flex items-center justify-center", role: "dialog", "aria-modal": "true", children: [_jsx("div", { className: "fixed inset-0 bg-black/50 backdrop-blur-sm", onClick: onClose }), _jsxs("div", { className: cn("relative bg-surface border border-border rounded-xl shadow-xl w-full mx-4", sizes[size]), children: [_jsxs("div", { className: "flex items-start justify-between p-5 border-b border-border", children: [_jsxs("div", { children: [_jsx("h2", { className: "text-base font-semibold text-text", children: title }), description && _jsx("p", { className: "text-sm text-text-muted mt-0.5", children: description })] }), _jsx("button", { onClick: onClose, className: "p-1 rounded-lg text-text-faint hover:text-text hover:bg-surface-2 transition-colors ml-auto", children: "\u2715" })] }), _jsx("div", { className: "p-5", children: children }), footer && (_jsx("div", { className: "flex items-center justify-end gap-2 p-4 border-t border-border bg-surface-2/50 rounded-b-xl", children: footer }))] })] }));
}
