import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useEffect, useState } from "react";
import { useI18n } from "../../context/I18nContext";
import { CommandPalette } from "./CommandPalette";
import { useTheme } from "../../context/ThemeContext";
export function TopBar({ onToggleSidebar, collapsed, }) {
    const { t, lang, setLang } = useI18n();
    const { resolved, setTheme } = useTheme();
    const [palOpen, setPalOpen] = useState(false);
    useEffect(() => {
        const handler = (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
                e.preventDefault();
                setPalOpen(true);
            }
        };
        window.addEventListener("keydown", handler);
        return () => window.removeEventListener("keydown", handler);
    }, []);
    return (_jsxs(_Fragment, { children: [_jsxs("header", { className: "top", children: [_jsx("button", { className: "iconbtn", onClick: onToggleSidebar, "aria-label": "Toggle sidebar", title: t("common.toggle_sidebar") || "Toggle sidebar", children: _jsx("svg", { className: "i", children: _jsx("use", { href: "#i-panel" }) }) }), _jsxs("div", { className: "brand", children: [_jsx("span", { className: "mark", "aria-hidden": "true", children: "\u00A7" }), _jsx("span", { className: "nm t", children: "Academic Research Assistant" })] }), _jsxs("button", { className: "proj", "aria-label": "Current project", children: [_jsx("span", { className: "faint t", children: "Project" }), _jsx("b", { children: "Hippocampal atrophy in MCI" }), _jsx("svg", { className: "i", children: _jsx("use", { href: "#i-down" }) })] }), _jsxs("button", { className: "searchbtn", onClick: () => setPalOpen(true), id: "openPal", children: [_jsx("svg", { className: "i", children: _jsx("use", { href: "#i-search" }) }), _jsx("span", { className: "t", children: "Search papers, journals, manuscripts\u2026" }), _jsx("kbd", { children: "Ctrl K" })] }), _jsxs("span", { className: "pill model", title: "Active AI model", children: [_jsx("svg", { className: "i", children: _jsx("use", { href: "#i-spark" }) }), _jsx("span", { className: "mono", children: "qwen2.5:14b" })] }), _jsxs("button", { className: "pill statusbtn", title: "System status", children: [_jsx("span", { className: "dot", id: "statusDot" }), _jsx("span", { className: "tx t", id: "statusTx", children: "All systems ready" })] }), _jsx("span", { className: "sample t", children: "Mockup \u00B7 sample data" }), _jsx("button", { className: "iconbtn", onClick: () => setLang(lang === "ar" ? "en" : "ar"), "aria-label": "Language", title: "English / \u0627\u0644\u0639\u0631\u0628\u064A\u0629", children: _jsx("svg", { className: "i", children: _jsx("use", { href: "#i-globe" }) }) }), _jsx("button", { className: "iconbtn", onClick: () => setTheme(resolved === "dark" ? "light" : "dark"), "aria-label": "Theme", title: "Light / Dark / System", children: _jsx("svg", { className: "i", children: _jsx("use", { href: resolved === "dark" ? "#i-sun" : "#i-moon" }) }) }), _jsxs("button", { className: "iconbtn bell", "aria-label": "Notifications", title: t("common.notifications"), children: [_jsx("svg", { className: "i", children: _jsx("use", { href: "#i-bell" }) }), _jsx("span", { className: "n", children: "3" })] }), _jsx("span", { className: "avatar", title: "Account", children: "MR" })] }), _jsx(CommandPalette, { open: palOpen, onClose: () => setPalOpen(false) })] }));
}
