import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from "react";
import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { Progress } from "../components/ui/Progress";
import { EmptyState } from "../components/ui/EmptyState";
import { Modal } from "../components/ui/Modal";
import { Alert } from "../components/ui/Alert";
import { Star, Loader2, ChevronRight, CheckCircle2, XCircle } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../components/ui/Toast";
import api from "../lib/api";
export default function EvaluationsPage() {
    const { t } = useI18n();
    const { addToast } = useToast();
    const [evaluations, setEvaluations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedEval, setSelectedEval] = useState(null);
    useEffect(() => {
        loadEvaluations();
    }, []);
    const loadEvaluations = async () => {
        try {
            const msRes = await api.get("/manuscripts?limit=20");
            const manuscripts = msRes.data.manuscripts || [];
            const evalPromises = manuscripts.map(async (ms) => {
                if (ms.analysis_status === "COMPLETED")
                    return null;
                try {
                    const res = await api.post(`/manuscripts/${ms.id}/evaluate`, { model: "qwen2.5:3b-instruct" });
                    return res.data;
                }
                catch {
                    return null;
                }
            });
            const results = await Promise.all(evalPromises);
            setEvaluations(results.filter(Boolean));
        }
        catch {
            // Silently handle error
        }
        finally {
            setLoading(false);
        }
    };
    const getScoreColor = (score) => {
        if (!score)
            return "text-text-muted";
        if (score >= 80)
            return "text-success";
        if (score >= 60)
            return "text-warning";
        return "text-error";
    };
    if (loading) {
        return (_jsxs("div", { className: "space-y-6 max-w-5xl", children: [_jsx(PageHeader, { title: t("evaluations.title"), subtitle: t("evaluations.subtitle") }), _jsx(Card, { children: _jsx("div", { className: "flex items-center justify-center py-12", children: _jsx(Loader2, { className: "w-8 h-8 animate-spin text-text-faint" }) }) })] }));
    }
    return (_jsxs("div", { className: "space-y-6 max-w-5xl", children: [_jsx(PageHeader, { title: t("evaluations.title"), subtitle: t("evaluations.subtitle") }), evaluations.length === 0 ? (_jsx(Card, { children: _jsx(EmptyState, { icon: _jsx(Star, { className: "w-10 h-10" }), title: t("evaluations.no_evaluations"), description: t("evaluations.no_evaluations_desc") }) })) : (_jsx("div", { className: "space-y-4", children: evaluations.map((evalItem) => (_jsx("div", { className: "bg-surface border border-border rounded-xl shadow-sm hover:border-primary/30 transition-colors cursor-pointer", onClick: () => setSelectedEval(evalItem), children: _jsxs("div", { className: "flex items-center justify-between gap-4 px-5 py-4", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: `w-10 h-10 rounded-lg flex items-center justify-center ${evalItem.final_status === "APPROVED" ? "bg-success-subtle" : evalItem.final_status === "REJECTED" ? "bg-error-subtle" : "bg-warning-subtle"}`, children: evalItem.final_status === "APPROVED" ? _jsx(CheckCircle2, { className: "w-5 h-5 text-success" }) : evalItem.final_status === "REJECTED" ? _jsx(XCircle, { className: "w-5 h-5 text-error" }) : _jsx(Star, { className: "w-5 h-5 text-warning" }) }), _jsxs("div", { children: [_jsxs("p", { className: "font-medium text-text", children: ["Evaluation #", evalItem.id] }), _jsxs("p", { className: "text-sm text-text-muted", children: [t("evaluations.journal"), ": ", evalItem.journal_id || "—", " \u2022 ", new Date(evalItem.created_at).toLocaleDateString()] })] })] }), _jsxs("div", { className: "flex items-center gap-4", children: [evalItem.scores?.compliance_score != null && (_jsxs("div", { className: "text-right", children: [_jsxs("p", { className: `text-lg font-semibold ${getScoreColor(evalItem.scores.compliance_score)}`, children: [evalItem.scores.compliance_score, "%"] }), _jsx("p", { className: "text-xs text-text-muted", children: t("evaluations.compliance") })] })), _jsx(Badge, { variant: evalItem.final_status === "APPROVED" ? "success" : evalItem.final_status === "REJECTED" ? "error" : "warning", children: evalItem.final_status || evalItem.status }), _jsx(ChevronRight, { className: "w-5 h-5 text-text-faint" })] })] }) }, evalItem.id))) })), _jsx(Modal, { open: !!selectedEval, onClose: () => setSelectedEval(null), title: t("evaluations.detail"), footer: _jsx(Button, { variant: "ghost", onClick: () => setSelectedEval(null), children: t("common.close") }), children: selectedEval && (_jsxs("div", { className: "space-y-4", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsx("span", { className: "text-sm font-medium text-text", children: t("manuscripts.overall_score") }), _jsxs("span", { className: `text-2xl font-bold ${getScoreColor(selectedEval.scores?.compliance_score)}`, children: [selectedEval.scores?.compliance_score ?? "—", "%"] })] }), _jsx(Progress, { value: selectedEval.scores?.compliance_score || 0, showLabel: true }), _jsx("div", { className: "grid grid-cols-2 gap-3", children: Object.entries(selectedEval.scores || {}).map(([key, value]) => (_jsxs("div", { className: "p-3 bg-surface-2 rounded-lg", children: [_jsx("p", { className: "text-xs text-text-muted capitalize", children: key.replace(/_/g, " ") }), _jsx("p", { className: "text-lg font-semibold text-text mt-1", children: value ?? "—" })] }, key))) }), _jsx(Alert, { variant: selectedEval.final_status === "APPROVED" ? "success" : selectedEval.final_status === "REJECTED" ? "error" : "warning", children: selectedEval.final_status || selectedEval.status })] })) })] }));
}
