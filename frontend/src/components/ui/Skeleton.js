import { jsx as _jsx } from "react/jsx-runtime";
export function Skeleton({ className, lines = 1 }) {
    if (lines > 1) {
        return (_jsx("div", { children: Array.from({ length: lines }).map((_, i) => (_jsx("div", { className: 'skel' + (className ? ' ' + className : ''), style: { marginBottom: i < lines - 1 ? 8 : 0 } }, i))) }));
    }
    return _jsx("div", { className: 'skel' + (className ? ' ' + className : '') });
}
