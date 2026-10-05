import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useLocation } from "react-router-dom";
import { useI18n } from "../../context/I18nContext";
const navGroups = [
    {
        title: "nav.group.work",
        items: [
            { id: "dashboard", label: "nav.dashboard", icon: "i-dash", path: "/" },
            { id: "papers", label: "nav.papers", icon: "i-paper", path: "/papers", count: 12 },
            { id: "journals", label: "nav.journals", icon: "i-journal", path: "/journals", count: 4 },
            { id: "manuscripts", label: "nav.manuscripts", icon: "i-edit", path: "/manuscripts", count: 2 },
        ],
    },
    {
        title: "nav.group.review",
        items: [
            { id: "compliance", label: "nav.compliance", icon: "i-shield", path: "/compliance", count: 2, countClass: "crit" },
            { id: "evaluations", label: "nav.evaluations", icon: "i-report", path: "/evaluations" },
            { id: "response-letters", label: "nav.response-letters", icon: "i-edit", path: "/response-letters" },
        ],
    },
];
export function Sidebar({ collapsed, onToggle }) {
    const { t } = useI18n();
    const location = useLocation();
    return (_jsxs("nav", { className: "side" + (collapsed ? " collapsed" : ""), "aria-label": "Main", children: [navGroups.map((group) => (_jsxs("div", { children: [!collapsed && _jsx("div", { className: "sec-label t", children: t(group.title) }), group.items.map((item) => {
                        const isActive = location.pathname === item.path;
                        return (_jsxs("button", { className: "nav" + (isActive ? " active" : ""), "data-go": item.path.replace("/", ""), "aria-current": isActive ? "page" : undefined, title: t(item.label), onClick: () => { window.location.href = item.path; }, children: [_jsx("svg", { className: "i", children: _jsx("use", { href: "#" + item.icon }) }), !collapsed && _jsx("span", { className: "lbl t", children: t(item.label) }), item.count !== undefined && (_jsx("span", { className: "cnt" + (item.countClass ? " " + item.countClass : ""), children: item.count }))] }, item.id));
                    })] }, group.title))), _jsx("div", { className: "grow" }), !collapsed && _jsx("div", { className: "sec-label t", children: "nav.group.system" }), _jsxs("button", { className: "nav", "data-go": "models", title: t("nav.models"), onClick: () => { window.location.href = "/models"; }, children: [_jsx("svg", { className: "i", children: _jsx("use", { href: "#i-cpu" }) }), !collapsed && _jsx("span", { className: "lbl t", children: t("nav.models") })] }), _jsxs("button", { className: "nav", "data-go": "chat", title: t("nav.chat"), onClick: () => { window.location.href = "/chat"; }, children: [_jsx("svg", { className: "i", children: _jsx("use", { href: "#i-comment" }) }), !collapsed && _jsx("span", { className: "lbl t", children: t("nav.chat") })] })] }));
}
