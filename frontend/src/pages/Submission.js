import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState } from "react";
import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { Input } from "../components/ui/Input";
import { Modal } from "../components/ui/Modal";
import { Loader2, Send, CheckCircle, XCircle } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../components/ui/Toast";
import api from "../lib/api";
export default function SubmissionPage() {
    const { t } = useI18n();
    const { addToast } = useToast();
    const [manuscriptId, setManuscriptId] = useState("");
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(false);
    const [showSubmitModal, setShowSubmitModal] = useState(false);
    const [changeSummary, setChangeSummary] = useState("");
    const [label, setLabel] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const loadStatus = async () => {
        if (!manuscriptId)
            return;
        setLoading(true);
        try {
            const res = await api.get(`/manuscripts/${manuscriptId}/submission/status`);
            setStatus(res.data);
        }
        catch {
            setStatus(null);
        }
        finally {
            setLoading(false);
        }
    };
    const handleSubmit = async () => {
        if (!manuscriptId)
            return;
        setSubmitting(true);
        try {
            await api.post(`/manuscripts/${manuscriptId}/submission`, {
                change_summary: changeSummary,
                label: label || undefined,
            });
            setShowSubmitModal(false);
            setChangeSummary("");
            setLabel("");
            loadStatus();
            addToast({ variant: "success", title: t("common.saved") });
        }
        catch {
            addToast({ variant: "error", title: t("common.error") });
        }
        finally {
            setSubmitting(false);
        }
    };
    return (_jsxs("div", { className: "space-y-6 max-w-5xl", children: [_jsx(PageHeader, { title: t("submission.title"), subtitle: t("submission.subtitle") }), _jsx(Card, { title: t("manuscripts.select"), children: _jsxs("div", { className: "flex gap-3", children: [_jsx(Input, { type: "number", placeholder: t("manuscripts.select"), value: manuscriptId, onChange: (e) => setManuscriptId(e.target.value), className: "flex-1" }), _jsxs(Button, { onClick: loadStatus, disabled: !manuscriptId || loading, children: [loading && _jsx(Loader2, { className: "w-4 h-4 animate-spin" }), t("journals.load")] })] }) }), status && (_jsxs(_Fragment, { children: [_jsxs("div", { className: "grid grid-cols-2 gap-4", children: [_jsx(Card, { className: status.ready_to_submit ? "border-success" : "", children: _jsxs("div", { className: "flex items-center gap-3", children: [status.ready_to_submit ? (_jsx(CheckCircle, { className: "w-8 h-8 text-success" })) : (_jsx(XCircle, { className: "w-8 h-8 text-error" })), _jsxs("div", { children: [_jsx("p", { className: "font-semibold text-text", children: status.ready_to_submit ? t("submission.ready_to_submit") : t("submission.not_ready") }), _jsx("p", { className: "text-sm text-text-muted", children: status.ready_to_submit ? t("submission.ready_desc") : t("submission.not_ready_desc") })] })] }) }), status.submitted_at && (_jsx(Card, { children: _jsxs("div", { className: "flex items-center gap-3", children: [_jsx(Send, { className: "w-8 h-8 text-info" }), _jsxs("div", { children: [_jsx("p", { className: "font-semibold text-text", children: t("submission.already_submitted") }), _jsx("p", { className: "text-sm text-text-muted", children: new Date(status.submitted_at).toLocaleString() })] })] }) }))] }), _jsx(Card, { title: t("submission.checklist"), children: _jsx("div", { className: "space-y-3", children: [
                                { key: "compliance_check", label: t("submission.compliance_check"), status: status.compliance_check },
                                { key: "improvements_addressed", label: t("submission.improvements_addressed"), status: status.improvements_addressed },
                                { key: "response_letters", label: t("submission.response_letters"), status: status.response_letters },
                                { key: "export_ready", label: t("submission.export_ready"), status: status.export_ready },
                            ].map((item) => (_jsxs("div", { className: "flex items-center justify-between p-3 bg-surface-2 rounded-lg", children: [_jsx("span", { className: "text-sm text-text", children: item.label }), _jsx(Badge, { variant: item.status ? "success" : "muted", children: item.status ? t("common.saved") : t("submission.not_ready") })] }, item.key))) }) }), !status.submitted_at && status.ready_to_submit && (_jsxs(Button, { size: "lg", onClick: () => setShowSubmitModal(true), children: [_jsx(Send, { className: "w-5 h-5" }), t("submission.submit")] }))] })), _jsx(Modal, { open: showSubmitModal, onClose: () => setShowSubmitModal(false), title: t("submission.submit"), footer: _jsxs(_Fragment, { children: [_jsx(Button, { variant: "ghost", onClick: () => setShowSubmitModal(false), children: t("common.cancel") }), _jsxs(Button, { onClick: handleSubmit, disabled: submitting, children: [submitting && _jsx(Loader2, { className: "w-4 h-4 animate-spin" }), t("submission.submit")] })] }), children: _jsxs("div", { className: "space-y-4", children: [_jsx(Input, { label: t("submission.change_summary"), value: changeSummary, onChange: (e) => setChangeSummary(e.target.value), placeholder: t("submission.change_summary_placeholder") }), _jsx(Input, { label: t("submission.label"), value: label, onChange: (e) => setLabel(e.target.value), placeholder: t("submission.label_placeholder") })] }) })] }));
}
