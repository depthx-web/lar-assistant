import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Card, PageHeader } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { Alert } from "../components/ui/Alert";
import api from "../lib/api";
import { useEffect, useState } from "react";
import { Activity, Database, HardDrive, Cpu, Loader2 } from "lucide-react";
import { useI18n } from "../context/I18nContext";
export default function StatusPage() {
    const { t } = useI18n();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    useEffect(() => {
        // System status endpoint may not exist, gracefully handle 404
        api.get("/system/status")
            .then((r) => { setData(r.data); setLoading(false); })
            .catch(() => {
            // If endpoint doesn't exist, show info that it's unavailable
            setLoading(false);
            setError(null);
            // Set data to null - we'll show the "not configured" state
        });
    }, []);
    if (loading) {
        return (_jsxs("div", { className: "space-y-6 max-w-5xl", children: [_jsx(PageHeader, { title: t("status.title"), subtitle: t("status.subtitle") }), _jsx("div", { className: "flex items-center justify-center py-20", children: _jsx(Loader2, { className: "w-8 h-8 animate-spin text-text-muted" }) })] }));
    }
    if (!data) {
        return (_jsxs("div", { className: "space-y-6 max-w-5xl", children: [_jsx(PageHeader, { title: t("status.title"), subtitle: t("status.subtitle") }), _jsxs(Card, { className: "text-center py-12", children: [_jsx("div", { className: "w-12 h-12 rounded-full bg-warning-subtle flex items-center justify-center mx-auto mb-3", children: _jsx("span", { className: "text-xl", children: "\u26A0" }) }), _jsx("p", { className: "text-sm font-medium text-text", children: t("status.unavailable") }), _jsx("p", { className: "text-xs text-text-muted mt-1", children: t("status.system_status_desc") })] })] }));
    }
    const components = data?.components ?? {};
    const isHealthy = data?.status === "ok";
    const componentIcons = {
        database: _jsx(Database, { className: "w-5 h-5" }),
        storage: _jsx(HardDrive, { className: "w-5 h-5" }),
        ollama: _jsx(Cpu, { className: "w-5 h-5" }),
        embedding: _jsx(Activity, { className: "w-5 h-5" }),
    };
    return (_jsxs("div", { className: "space-y-6 max-w-5xl", children: [_jsx(PageHeader, { title: t("status.title"), subtitle: t("status.subtitle") }), _jsxs("div", { className: "grid grid-cols-2 gap-4", children: [_jsxs(Card, { className: "text-center", children: [_jsxs("div", { className: "flex items-center justify-center gap-2 mb-2", children: [isHealthy
                                        ? _jsx("span", { className: "w-3 h-3 rounded-full bg-success" })
                                        : _jsx("span", { className: "w-3 h-3 rounded-full bg-warning" }), _jsx("span", { className: "text-lg font-semibold text-text capitalize", children: data?.status || "unknown" })] }), _jsx("p", { className: "text-xs text-text-muted", children: t("status.overall_status") })] }), _jsxs(Card, { className: "text-center", children: [_jsxs("div", { className: "flex items-center justify-center gap-2 mb-2", children: [data?.uptime_check
                                        ? _jsx("span", { className: "text-success", children: "\u2713" })
                                        : _jsx("span", { className: "text-error", children: "\u2717" }), _jsx("span", { className: "text-lg font-semibold text-text", children: t("status.uptime_check") })] }), _jsx("p", { className: "text-xs text-text-muted", children: t("status.service_connectivity") })] })] }), _jsx(Card, { title: t("status.component_health"), children: _jsx("div", { className: "space-y-4", children: Object.entries(components).map(([key, comp]) => (_jsxs("div", { className: "flex items-center justify-between py-2 border-b border-border last:border-0", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx("span", { className: "text-text-muted", children: componentIcons[key] || _jsx(Activity, { className: "w-5 h-5" }) }), _jsxs("div", { children: [_jsx("p", { className: "text-sm font-medium text-text", children: comp.name || key }), comp.detail && (_jsx("p", { className: "text-xs text-text-muted mt-0.5", children: comp.detail }))] })] }), _jsx(Badge, { variant: comp.status === "ok" ? "success" : comp.status === "error" ? "error" : "warning", children: comp.status })] }, key))) }) }), !isHealthy && (_jsx(Alert, { variant: "warning", title: t("status.system_degraded"), children: t("status.system_degraded_desc") }))] }));
}
