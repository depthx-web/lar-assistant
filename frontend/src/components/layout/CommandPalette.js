import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useI18n } from "../../context/I18nContext";
const COMMANDS = [
    { id: "dashboard", label: "nav.dashboard", path: "/", icon: "i-dash", hint: "Cmd D" },
    { id: "papers", label: "nav.papers", path: "/papers", icon: "i-paper", hint: "Cmd P" },
    { id: "journals", label: "nav.journals", path: "/journals", icon: "i-journal", hint: "Cmd J" },
    { id: "manuscripts", label: "nav.manuscripts", path: "/manuscripts", icon: "i-edit", hint: "Cmd M" },
    { id: "workflow", label: "nav.workflow", path: "/workflow", icon: "i-spark", hint: "Cmd W" },
    { id: "evaluations", label: "nav.evaluations", path: "/evaluations", icon: "i-report", hint: "Cmd E" },
    { id: "compliance", label: "nav.compliance", path: "/compliance", icon: "i-shield", hint: "Cmd C" },
    { id: "response", label: "nav.response-letters", path: "/response-letters", icon: "i-edit", hint: "Cmd R" },
    { id: "improvements", label: "nav.improvements", path: "/improvements", icon: "i-spark", hint: "Cmd I" },
    { id: "tags", label: "nav.tags-comments", path: "/tags-comments", icon: "i-list", hint: "Cmd T" },
    { id: "diff", label: "nav.diff", path: "/diff", icon: "i-copy", hint: "" },
    { id: "exports", label: "nav.exports", path: "/exports", icon: "i-upload", hint: "" },
    { id: "submission", label: "nav.submission", path: "/submission", icon: "i-send", hint: "" },
    { id: "models", label: "nav.models", path: "/models", icon: "i-cpu", hint: "Cmd O" },
    { id: "status", label: "nav.status", path: "/status", icon: "i-spark", hint: "Cmd S" },
    { id: "chat", label: "nav.chat", path: "/chat", icon: "i-comment", hint: "Cmd K" },
];
export function CommandPalette({ open, onClose }) {
    const [query, setQuery] = useState("");
    const [active, setActive] = useState(0);
    const inputRef = useRef(null);
    const navigate = useNavigate();
    const { t } = useI18n();
    const results = COMMANDS.filter((c) => t(c.label).toLowerCase().includes(query.toLowerCase()));
    useEffect(() => {
        if (open) {
            setQuery("");
            setActive(0);
        }
    }, [open]);
    if (!open)
        return null;
    const run = (c) => {
        navigate(c.path);
        onClose();
    };
    const handleKey = (e) => {
        if (e.key === "ArrowDown") {
            e.preventDefault();
            setActive((a) => Math.min(a + 1, results.length - 1));
        }
        else if (e.key === "ArrowUp") {
            e.preventDefault();
            setActive((a) => Math.max(a - 1, 0));
        }
        else if (e.key === "Enter" && results[active]) {
            e.preventDefault();
            run(results[active]);
        }
    };
    return (_jsx("div", { className: "scrim", onClick: onClose, children: _jsxs("div", { className: "pal", onClick: (e) => e.stopPropagation(), role: "dialog", "aria-modal": "true", children: [_jsx("input", { ref: inputRef, value: query, onChange: (e) => { setQuery(e.target.value); setActive(0); }, onKeyDown: handleKey, placeholder: t("palette.placeholder") || "Search..." }), _jsx("ul", { children: results.length === 0 ? (_jsx("li", { children: _jsx("button", { style: { color: "var(--ink-3)", fontStyle: "italic", padding: "8px 14px" }, children: t("common.no_results") || "No results" }) })) : (results.map((c, i) => (_jsx("li", { children: _jsxs("button", { onClick: () => run(c), onMouseEnter: () => setActive(i), className: i === active ? "act" : "", children: [_jsx("svg", { className: "i", children: _jsx("use", { href: "#" + c.icon }) }), _jsx("span", { children: t(c.label) }), c.hint && _jsx("kbd", { children: c.hint })] }) }, c.id)))) }), _jsxs("div", { className: "hint", children: [_jsxs("span", { children: [_jsx("kbd", { children: "\u2191" }), _jsx("kbd", { children: "\u2193" }), " ", t("palette.navigate") || "Navigate"] }), _jsxs("span", { children: [_jsx("kbd", { children: "Enter" }), " ", t("palette.open") || "Open"] }), _jsxs("span", { style: { marginLeft: "auto" }, children: [_jsx("kbd", { children: "Esc" }), " ", t("common.close") || "Close"] })] })] }) }));
}
