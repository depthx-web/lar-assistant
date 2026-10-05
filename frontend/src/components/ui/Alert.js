import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { AlertCircle, CheckCircle2, XCircle, Info } from "lucide-react";
import { cn } from "./cn";
const variants = {
    info: {
        icon: _jsx(Info, { className: "h-4 w-4" }),
        bg: "bg-info-subtle",
        border: "border-info/20",
        text: "text-info",
    },
    success: {
        icon: _jsx(CheckCircle2, { className: "h-4 w-4" }),
        bg: "bg-success-subtle",
        border: "border-success/20",
        text: "text-success",
    },
    warning: {
        icon: _jsx(AlertCircle, { className: "h-4 w-4" }),
        bg: "bg-warning-subtle",
        border: "border-warning/20",
        text: "text-warning",
    },
    error: {
        icon: _jsx(XCircle, { className: "h-4 w-4" }),
        bg: "bg-error-subtle",
        border: "border-error/20",
        text: "text-error",
    },
};
export function Alert({ variant = "info", title, children, className }) {
    const v = variants[variant];
    return (_jsxs("div", { className: cn("flex gap-3 p-4 rounded-lg border", v.bg, v.border, className), children: [_jsx("span", { className: cn("shrink-0 mt-0.5", v.text), children: v.icon }), _jsxs("div", { children: [title && _jsx("p", { className: cn("font-medium text-sm", v.text), children: title }), _jsx("p", { className: "text-sm text-text-muted mt-0.5", children: children })] })] }));
}
