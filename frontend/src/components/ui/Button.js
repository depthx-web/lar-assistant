import { jsx as _jsx } from "react/jsx-runtime";
export function Button({ variant = "secondary", size = "md", loading = false, disabled, className, children, ...props }) {
    const classes = {
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
    return (_jsx("button", { className: combined, disabled: disabled || loading, ...props, children: children }));
}
