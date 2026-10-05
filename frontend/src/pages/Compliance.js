import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Card, PageHeader } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { Skeleton } from "../components/ui/Skeleton";
import { EmptyState } from "../components/ui/EmptyState";
import { Alert } from "../components/ui/Alert";
import api from "../lib/api";
import { useEffect, useState } from "react";
import { FileText } from "lucide-react";
import { useI18n } from "../context/I18nContext";
export default function CompliancePage() {
    const { t } = useI18n();
    const [queue, setQueue] = useState(null);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        api.get("/system/queue")
            .then((r) => { setQueue(r.data); setLoading(false); })
            .catch(() => setLoading(false));
    }, []);
    return (_jsxs("div", { className: "space-y-6 max-w-5xl", children: [_jsx(PageHeader, { title: t("compliance.title"), subtitle: t("compliance.subtitle") }), _jsxs("div", { className: "grid grid-cols-3 gap-4", children: [_jsxs(Card, { className: "text-center", children: [_jsx("p", { className: "text-3xl font-semibold text-text", children: "\u2014" }), _jsx("p", { className: "text-xs text-text-muted mt-1", children: t("compliance.ready") })] }), _jsxs(Card, { className: "text-center", children: [_jsx("p", { className: "text-3xl font-semibold text-warning", children: "\u2014" }), _jsx("p", { className: "text-xs text-text-muted mt-1", children: t("compliance.needs_review") })] }), _jsxs(Card, { className: "text-center", children: [_jsx("p", { className: "text-3xl font-semibold text-success", children: "\u2014" }), _jsx("p", { className: "text-xs text-text-muted mt-1", children: t("compliance.submitted") })] })] }), _jsx(Card, { title: t("compliance.processing_queue"), children: loading ? (_jsx("div", { className: "space-y-2", children: [1, 2, 3].map((i) => _jsx(Skeleton, { className: "h-10" }, i)) })) : !queue || queue.jobs.length === 0 ? (_jsx(EmptyState, { icon: _jsx(FileText, { className: "w-8 h-8 text-text-faint" }), title: t("compliance.queue_empty"), description: t("compliance.queue_empty_desc") })) : (_jsx("div", { className: "space-y-2", children: queue.jobs.map((job) => (_jsxs("div", { className: "flex items-center gap-4 p-3 bg-surface-2 rounded-lg", children: [_jsxs("span", { className: "text-xs font-mono text-text-muted w-8", children: ["#", job.id] }), _jsx("span", { className: "text-sm font-medium text-text flex-1", children: job.job_type }), _jsx(Badge, { variant: job.status === "SUCCEEDED" ? "success" : job.status === "FAILED" ? "error" : job.status === "RUNNING" ? "warning" : "muted", children: job.status }), _jsx("span", { className: "text-xs text-text-faint", children: new Date(job.created_at).toLocaleTimeString() })] }, job.id))) })) }), _jsx(Alert, { variant: "info", title: t("compliance.how_it_works"), children: t("compliance.how_it_works_desc") })] }));
}
