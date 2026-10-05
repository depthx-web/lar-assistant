import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
export function Card({ children, className, title, subtitle, action }) {
    return (_jsxs("div", { className: "box" + (className ? " " + className : ""), children: [(title || subtitle || action) && (_jsxs("header", { children: [_jsxs("div", { children: [title && _jsx("h2", { children: title }), subtitle && _jsx("p", { className: "faint", children: subtitle })] }), action && _jsx("div", { children: action })] })), _jsx("div", { className: "in", children: children })] }));
}
export function PageHeader({ title, subtitle, action }) {
    return (_jsxs("div", { className: "pagehead", children: [_jsxs("div", { children: [_jsx("h1", { children: title }), subtitle && _jsx("p", { className: "sub", children: subtitle })] }), action && _jsx("div", { className: "actions", children: action })] }));
}
