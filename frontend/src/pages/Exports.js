import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { Progress } from "../components/ui/Progress";
import { EmptyState } from "../components/ui/EmptyState";
import { Loader2, Download, Plus } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../components/ui/Toast";
import api from "../lib/api";
const FORMATS = ["pdf", "docx", "markdown", "tex"];
export default function ExportsPage() {
    const { t } = useI18n();
    const { addToast } = useToast();
    const [manuscriptId, setManuscriptId] = useState("");
    const [exports, setExports] = useState([]);
    const [loading, setLoading] = useState(false);
    const [creating, setCreating] = useState(false);
    const [selectedFormat, setSelectedFormat] = useState("pdf");
    const loadExports = async () => {
        if (!manuscriptId)
            return;
        setLoading(true);
        try {
            const res = await api.get(`/manuscripts/${manuscriptId}/exports`);
            setExports(res.data.jobs || []);
        }
        catch {
            setExports([]);
        }
        finally {
            setLoading(false);
        }
    };
    const handleCreate = async () => {
        if (!manuscriptId)
            return;
        setCreating(true);
        try {
            await api.post(`/manuscripts/${manuscriptId}/export`, { format: selectedFormat, version_id: null });
            addToast({ variant: "success", title: t("common.saved") });
            loadExports();
        }
        catch {
            addToast({ variant: "error", title: t("common.error") });
        }
        finally {
            setCreating(false);
        }
    };
    const handleRun = async (jobId) => {
        try {
            await api.post(`/manuscripts/${manuscriptId}/export/${jobId}/run`, {});
            loadExports();
        }
        catch {
            addToast({ variant: "error", title: t("common.error") });
        }
    };
    return (_jsxs("div", { className: "space-y-6 max-w-5xl", children: [_jsx(PageHeader, { title: t("exports.title"), subtitle: t("exports.subtitle") }), _jsx(Card, { title: t("exports.export"), children: _jsxs("div", { className: "flex gap-3 items-end", children: [_jsxs("div", { className: "flex-1", children: [_jsx("label", { className: "text-sm font-medium text-text mb-1 block", children: t("manuscripts.select") }), _jsx("input", { type: "number", value: manuscriptId, onChange: (e) => setManuscriptId(e.target.value), className: "w-full px-3 py-2 text-sm bg-surface border border-border rounded-lg text-text placeholder-text-faint focus:border-primary focus:ring-1 focus:ring-primary", placeholder: t("manuscripts.select") })] }), _jsxs("div", { children: [_jsx("label", { className: "text-sm font-medium text-text mb-1 block", children: t("exports.export_format") }), _jsx("select", { value: selectedFormat, onChange: (e) => setSelectedFormat(e.target.value), className: "px-3 py-2 text-sm bg-surface border border-border rounded-lg text-text focus:border-primary focus:ring-1 focus:ring-primary", children: FORMATS.map((f) => _jsx("option", { value: f, children: f.toUpperCase() }, f)) })] }), _jsxs(Button, { onClick: handleCreate, disabled: creating || !manuscriptId, children: [creating && _jsx(Loader2, { className: "w-4 h-4 animate-spin" }), _jsx(Plus, { className: "w-4 h-4" }), t("exports.export")] }), _jsxs(Button, { variant: "secondary", onClick: loadExports, disabled: loading || !manuscriptId, children: [loading && _jsx(Loader2, { className: "w-4 h-4 animate-spin" }), t("journals.load")] })] }) }), manuscriptId && !loading && exports.length === 0 ? (_jsx(Card, { children: _jsx(EmptyState, { icon: _jsx(Download, { className: "w-10 h-10" }), title: t("exports.no_exports"), description: t("exports.no_exports_desc") }) })) : (_jsx("div", { className: "space-y-3", children: exports.map((job) => (_jsxs("div", { className: "bg-surface border border-border rounded-xl p-4", children: [_jsxs("div", { className: "flex items-center justify-between mb-2", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx(Badge, { variant: "info", children: job.format.toUpperCase() }), _jsxs("span", { className: "text-sm text-text-muted", children: ["#", job.id] })] }), _jsx(Badge, { variant: job.status === "COMPLETED" ? "success" :
                                        job.status === "RUNNING" ? "warning" :
                                            job.status === "FAILED" ? "error" : "muted", children: job.status })] }), _jsx(Progress, { value: job.progress, className: "mb-2", showLabel: true }), _jsxs("div", { className: "flex justify-end gap-2", children: [job.status === "PENDING" && (_jsx(Button, { size: "sm", onClick: () => handleRun(job.id), children: t("exports.run") })), job.status === "COMPLETED" && (_jsxs(Button, { size: "sm", variant: "secondary", onClick: () => addToast({ variant: "info", title: t("exports.download_started") }), children: [_jsx(Download, { className: "w-4 h-4" }), t("exports.download")] }))] })] }, job.id))) }))] }));
}
