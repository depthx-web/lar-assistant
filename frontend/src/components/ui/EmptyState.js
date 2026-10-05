import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
export function EmptyState({ icon, title, description, action }) {
    return (_jsxs("div", { style: { textAlign: 'center', padding: '48px 0' }, children: [icon && _jsx("div", { style: { marginBottom: 16 }, children: icon }), _jsx("p", { style: { color: 'var(--ink-2)' }, children: title }), description && _jsx("p", { style: { fontSize: 12.5, color: 'var(--ink-3)', marginTop: 8 }, children: description }), action && _jsx("div", { style: { marginTop: 24 }, children: action })] }));
}
