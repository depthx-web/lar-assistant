import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect } from "react";
import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { Modal } from "../components/ui/Modal";
import { EmptyState } from "../components/ui/EmptyState";
import { Badge } from "../components/ui/Badge";
import { Progress } from "../components/ui/Progress";
import { ScrollText, Plus, Loader2, XCircle, Play } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../components/ui/Toast";
import api from "../lib/api";
export default function ManuscriptsPage() {
    const { t } = useI18n();
    const { addToast } = useToast();
    const [manuscripts, setManuscripts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [modalOpen, setModalOpen] = useState(false);
    const [title, setTitle] = useState("");
    const [journalId, setJournalId] = useState("");
    const [paperId, setPaperId] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const [analyzingId, setAnalyzingId] = useState(null);
    useEffect(() => {
        loadManuscripts();
    }, []);
    const loadManuscripts = async () => {
        try {
            const res = await api.get("/manuscripts");
            setManuscripts(res.data.manuscripts || []);
        }
        catch {
            // Silently handle error
        }
        finally {
            setLoading(false);
        }
    };
    const handleCreate = async () => {
        if (!title.trim()) {
            addToast({ variant: "warning", title: t("common.required") });
            return;
        }
        setSubmitting(true);
        try {
            await api.post("/manuscripts", {
                title: title.trim(),
                journal_id: journalId ? Number(journalId) : null,
                document_id: paperId ? Number(paperId) : null,
            });
            addToast({ variant: "success", title: t("manuscripts.created") });
            setModalOpen(false);
            setTitle("");
            setJournalId("");
            setPaperId("");
            loadManuscripts();
        }
        catch {
            addToast({ variant: "error", title: t("common.error"), description: t("manuscripts.create_failed") });
        }
        finally {
            setSubmitting(false);
        }
    };
    const handleAnalyze = async (id) => {
        setAnalyzingId(id);
        try {
            await api.post(`/manuscripts/${id}/analyze`);
            addToast({ variant: "success", title: t("manuscripts.analyzed") });
            loadManuscripts();
        }
        catch (err) {
            addToast({ variant: "error", title: t("common.error"), description: err.response?.data?.detail ?? "Analysis failed" });
        }
        finally {
            setAnalyzingId(null);
        }
    };
    const handleDelete = async (id) => {
        if (!confirm(t("manuscripts.confirm_delete")))
            return;
        try {
            await api.delete(`/manuscripts/${id}`);
            addToast({ variant: "success", title: t("manuscripts.deleted") });
            loadManuscripts();
        }
        catch {
            addToast({ variant: "error", title: t("common.error"), description: t("manuscripts.delete_failed") });
        }
    };
    if (loading) {
        return (_jsxs("div", { className: "space-y-6 max-w-5xl", children: [_jsx(PageHeader, { title: t("manuscripts.title"), subtitle: t("manuscripts.subtitle") }), _jsx(Card, { children: _jsx("div", { className: "flex items-center justify-center py-12", children: _jsx(Loader2, { className: "w-8 h-8 animate-spin text-text-faint" }) }) })] }));
    }
    return (_jsxs("div", { className: "space-y-6 max-w-5xl", children: [_jsx(PageHeader, { title: t("manuscripts.title"), subtitle: t("manuscripts.subtitle"), action: _jsxs(Button, { onClick: () => setModalOpen(true), children: [_jsx(Plus, { className: "w-4 h-4" }), t("manuscripts.new")] }) }), manuscripts.length === 0 ? (_jsx(Card, { children: _jsx(EmptyState, { icon: _jsx(ScrollText, { className: "w-10 h-10" }), title: t("manuscripts.no_manuscripts"), description: t("manuscripts.no_manuscripts_desc"), action: _jsxs(Button, { onClick: () => setModalOpen(true), children: [_jsx(Plus, { className: "w-4 h-4" }), t("manuscripts.new")] }) }) })) : (_jsx("div", { className: "space-y-4", children: manuscripts.map((ms) => (_jsx(Card, { className: "hover:border-primary/30 transition-colors", children: _jsxs("div", { className: "flex items-start justify-between gap-4", children: [_jsxs("div", { className: "flex-1 min-w-0", children: [_jsxs("div", { className: "flex items-center gap-2 mb-1", children: [_jsx(ScrollText, { className: "w-4 h-4 text-text-faint" }), _jsx("h3", { className: "font-semibold text-text truncate", children: ms.title }), _jsxs("span", { className: "text-xs text-text-faint", children: ["#", ms.id] })] }), _jsxs("div", { className: "flex items-center gap-4 text-sm text-text-muted mt-2", children: [ms.journal_id && (_jsxs("span", { children: [t("manuscripts.journal"), ": ", ms.journal_id] })), ms.document_id && (_jsxs("span", { children: [t("manuscripts.paper"), ": ", ms.document_id] })), _jsx("span", { children: new Date(ms.created_at).toLocaleDateString() })] }), ms.overall_compliance_score != null && (_jsxs("div", { className: "mt-3 flex items-center gap-3", children: [_jsx(Progress, { value: ms.overall_compliance_score ?? 0, size: "sm", className: "w-32" }), _jsxs("span", { className: `text-sm font-medium ${ms.overall_compliance_score >= 80 ? "text-success" : ms.overall_compliance_score >= 60 ? "text-warning" : "text-error"}`, children: [Math.round(ms.overall_compliance_score * 100), "%"] }), _jsx(Badge, { variant: ms.analysis_status === "COMPLETED" ? "success" : ms.analysis_status === "PROCESSING" ? "warning" : "muted", children: ms.analysis_status || "PENDING" })] }))] }), _jsxs("div", { className: "flex items-center gap-2 shrink-0", children: [ms.analysis_status !== "COMPLETED" && (_jsx(Button, { variant: "ghost", size: "sm", onClick: () => handleAnalyze(ms.id), title: "Analyze manuscript", loading: analyzingId === ms.id, children: _jsx(Play, { className: "w-4 h-4" }) })), _jsx(Button, { variant: "ghost", size: "sm", onClick: () => handleDelete(ms.id), title: t("common.delete"), className: "text-error hover:text-error", children: _jsx(XCircle, { className: "w-4 h-4" }) })] })] }) }, ms.id))) })), _jsx(Modal, { open: modalOpen, onClose: () => setModalOpen(false), title: t("manuscripts.new"), description: t("manuscripts.new_desc"), footer: _jsxs(_Fragment, { children: [_jsx(Button, { variant: "ghost", onClick: () => setModalOpen(false), children: t("common.cancel") }), _jsxs(Button, { onClick: handleCreate, disabled: submitting, children: [submitting && _jsx(Loader2, { className: "w-4 h-4 animate-spin" }), t("manuscripts.create")] })] }), children: _jsxs("div", { className: "space-y-4", children: [_jsx(Input, { label: t("manuscripts.title"), value: title, onChange: (e) => setTitle(e.target.value), placeholder: t("manuscripts.title_placeholder") }), _jsx(Input, { label: t("manuscripts.paper"), value: paperId, onChange: (e) => setPaperId(e.target.value), placeholder: t("manuscripts.paper_placeholder"), helper: t("manuscripts.paper_helper") }), _jsx(Input, { label: t("manuscripts.journal"), value: journalId, onChange: (e) => setJournalId(e.target.value), placeholder: t("manuscripts.journal_placeholder") })] }) })] }));
}
