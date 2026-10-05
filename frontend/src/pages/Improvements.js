import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { EmptyState } from "../components/ui/EmptyState";
import { Modal } from "../components/ui/Modal";
import { Loader2, Lightbulb, CheckCircle2 } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../components/ui/Toast";
import api from "../lib/api";
export default function ImprovementsPage() {
    const { t } = useI18n();
    const { addToast } = useToast();
    const [manuscriptId, setManuscriptId] = useState("");
    const [suggestions, setSuggestions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [generating, setGenerating] = useState(false);
    const [selectedSuggestion, setSelectedSuggestion] = useState(null);
    const loadSuggestions = async () => {
        if (!manuscriptId)
            return;
        setLoading(true);
        try {
            const res = await api.get(`/manuscripts/${manuscriptId}/improvements`);
            setSuggestions(res.data.suggestions || []);
        }
        catch {
            setSuggestions([]);
        }
        finally {
            setLoading(false);
        }
    };
    const handleGenerate = async () => {
        if (!manuscriptId)
            return;
        setGenerating(true);
        try {
            const res = await api.post(`/manuscripts/${manuscriptId}/improvements/generate`, {
                evaluation_id: null,
                force_regenerate: false,
            });
            setSuggestions(res.data.suggestions || []);
            addToast({ variant: "success", title: t("common.saved") });
        }
        catch (err) {
            addToast({
                variant: "error",
                title: t("common.error"),
                description: err.response?.data?.detail || t("common.error"),
            });
        }
        finally {
            setGenerating(false);
        }
    };
    const handleAddress = async (suggestionId) => {
        try {
            await api.post(`/manuscripts/${manuscriptId}/improvements/${suggestionId}/address`, {
                version_id: null,
                reviewer: "user",
            });
            loadSuggestions();
            setSelectedSuggestion(null);
            addToast({ variant: "success", title: t("common.saved") });
        }
        catch {
            addToast({ variant: "error", title: t("common.error") });
        }
    };
    const addressedCount = suggestions.filter((s) => s.status === "ADDRESSED").length;
    const pendingCount = suggestions.filter((s) => s.status !== "ADDRESSED").length;
    return (_jsxs("div", { className: "space-y-6 max-w-5xl", children: [_jsx(PageHeader, { title: t("improvements.title"), subtitle: t("improvements.subtitle") }), _jsx(Card, { title: t("manuscripts.select"), children: _jsxs("div", { className: "flex gap-3", children: [_jsx("input", { type: "number", placeholder: t("manuscripts.select"), value: manuscriptId, onChange: (e) => setManuscriptId(e.target.value), className: "flex-1 px-3 py-2 text-sm bg-surface border border-border rounded-lg text-text placeholder-text-faint focus:border-primary focus:ring-1 focus:ring-primary" }), _jsxs(Button, { onClick: loadSuggestions, disabled: !manuscriptId || loading, children: [loading && _jsx(Loader2, { className: "w-4 h-4 animate-spin" }), t("journals.load")] }), _jsxs(Button, { variant: "secondary", onClick: handleGenerate, disabled: generating || !manuscriptId, children: [generating && _jsx(Loader2, { className: "w-4 h-4 animate-spin" }), _jsx(Lightbulb, { className: "w-4 h-4" }), t("improvements.generate")] })] }) }), suggestions.length > 0 && (_jsxs("div", { className: "grid grid-cols-3 gap-4", children: [_jsxs(Card, { className: "text-center", children: [_jsx("p", { className: "text-3xl font-semibold text-text", children: suggestions.length }), _jsx("p", { className: "text-xs text-text-muted mt-1", children: t("improvements.total") })] }), _jsxs(Card, { className: "text-center border-success", children: [_jsx("p", { className: "text-3xl font-semibold text-success", children: addressedCount }), _jsx("p", { className: "text-xs text-text-muted mt-1", children: t("improvements.addressed_count") })] }), _jsxs(Card, { className: "text-center border-warning", children: [_jsx("p", { className: "text-3xl font-semibold text-warning", children: pendingCount }), _jsx("p", { className: "text-xs text-text-muted mt-1", children: t("improvements.pending_count") })] })] })), loading ? (_jsx(Card, { children: _jsx("div", { className: "flex items-center justify-center py-12", children: _jsx(Loader2, { className: "w-8 h-8 animate-spin text-text-faint" }) }) })) : suggestions.length === 0 ? (_jsx(Card, { children: _jsx(EmptyState, { icon: _jsx(Lightbulb, { className: "w-10 h-10" }), title: t("improvements.no_suggestions"), description: t("improvements.no_suggestions_desc") }) })) : (_jsx("div", { className: "space-y-3", children: suggestions.map((s) => (_jsx("div", { className: "bg-surface border border-border rounded-xl shadow-sm hover:border-primary/30 transition-colors cursor-pointer", onClick: () => setSelectedSuggestion(s), children: _jsxs("div", { className: "flex items-center justify-between gap-4 px-5 py-4", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx(Badge, { variant: s.severity === "critical" ? "error" :
                                            s.severity === "warning" ? "warning" : "info", children: s.severity }), _jsx("span", { className: "text-sm text-text-muted capitalize", children: s.suggestion_type }), _jsx("p", { className: "text-sm text-text", children: s.description })] }), _jsx(Badge, { variant: s.status === "ADDRESSED" ? "success" : "warning", children: s.status === "ADDRESSED" ? t("improvements.addressed") : t("improvements.pending") })] }) }, s.id))) })), _jsx(Modal, { open: !!selectedSuggestion, onClose: () => setSelectedSuggestion(null), title: `${t("tags_comments.comment_text")}: ${selectedSuggestion?.id}`, footer: _jsxs("div", { className: "flex gap-2", children: [_jsx(Button, { variant: "ghost", onClick: () => setSelectedSuggestion(null), children: t("common.close") }), selectedSuggestion?.status !== "ADDRESSED" && (_jsxs(Button, { onClick: () => selectedSuggestion && handleAddress(selectedSuggestion.id), children: [_jsx(CheckCircle2, { className: "w-4 h-4" }), t("improvements.address")] }))] }), children: selectedSuggestion && (_jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "flex gap-2", children: [_jsx(Badge, { variant: selectedSuggestion.severity === "critical" ? "error" : selectedSuggestion.severity === "warning" ? "warning" : "info", children: selectedSuggestion.severity }), _jsx(Badge, { variant: "info", children: selectedSuggestion.suggestion_type }), _jsx(Badge, { variant: selectedSuggestion.status === "ADDRESSED" ? "success" : "warning", children: selectedSuggestion.status })] }), _jsx("p", { className: "text-text", children: selectedSuggestion.description }), selectedSuggestion.suggested_fix && (_jsxs("div", { className: "p-4 bg-surface-2 rounded-lg", children: [_jsx("p", { className: "text-sm font-medium text-text mb-2", children: t("tags_comments.comment_text") }), _jsx("p", { className: "text-sm text-text-muted whitespace-pre-wrap", children: selectedSuggestion.suggested_fix })] }))] })) })] }));
}
