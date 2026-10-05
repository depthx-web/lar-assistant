import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
export function Progress({ value = 0, max = 100, className, showLabel, size = 'md' }) {
    const pct = Math.round((value / max) * 100);
    const height = size === 'sm' ? 4 : 6;
    return (_jsxs("div", { className: 'prog' + (className ? ' ' + className : ''), style: { height }, children: [_jsx("i", { style: { width: pct + '%' } }), showLabel && _jsx("span", { className: 'v', style: { fontSize: 11, marginTop: 4 }, children: pct + '%' })] }));
}
