import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
export function Input({ label, value, onChange, placeholder, type = 'text', helper, className }) {
    return (_jsxs("div", { className: className, children: [label && _jsx("label", { className: 't', style: { display: 'block', fontSize: 12.5, color: 'var(--ink-2)', marginBottom: 4 }, children: label }), _jsx("input", { type: type, value: value, onChange: onChange, placeholder: placeholder, className: 'field', style: { width: '100%' } }), helper && _jsx("span", { className: 'faint', style: { fontSize: 11.5, marginTop: 4, display: 'block' }, children: helper })] }));
}
