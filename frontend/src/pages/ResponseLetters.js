import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from "react";
import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { EmptyState } from "../components/ui/EmptyState";
import { Modal } from "../components/ui/Modal";
import { FileText, Plus, Loader2, Eye, RefreshCw } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../components/ui/Toast";
import api from "../lib/api";
export default function ResponseLettersPage() {
    const { t } = useI18n();
    const { addToast } = useToast();
    const [letters, setLetters] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedLetter, setSelectedLetter] = useState(null);
    const [generating, setGenerating] = useState(false);
    const [manuscriptId, setManuscriptId] = useState("");
    useEffect(() => {
        if (manuscriptId)
            loadLetters();
    }, [manuscriptId]);
    const loadLetters = async () => {
        if (!manuscriptId)
            return;
        setLoading(true);
        try {
            const res = await api.get(`/manuscripts/${manuscriptId}/response-letters`);
            setLetters(res.data.letters || []);
        }
        catch {
            setLetters([]);
        }
        finally {
            setLoading(false);
        }
    };
    const handleGenerate = async () => {
        if (!manuscriptId) {
            addToast({ variant: "warning", title: t("response_letters.enter_manuscript") });
            return;
        }
        setGenerating(true);
        try {
            const res = await api.post(`/manuscripts/${manuscriptId}/response-letters/generate`, {});
            setLetters([res.data, ...letters]);
            addToast({ variant: "success", title: t("response_letters.generated") });
        }
        catch {
            addToast({ variant: "error", title: t("common.error"), description: t("response_letters.generate_failed") });
        }
        finally {
            setGenerating(false);
        }
    };
    if (loading && letters.length === 0) {
        return (_jsxs("div", { className: "space-y-6 max-w-5xl", children: [_jsx(PageHeader, { title: t("response_letters.title"), subtitle: t("response_letters.subtitle") }), _jsx(Card, { children: _jsx("div", { className: "flex items-center justify-center py-12", children: _jsx(Loader2, { className: "w-8 h-8 animate-spin text-text-faint" }) }) })] }));
    }
    return (_jsxs("div", { className: "space-y-6 max-w-5xl", children: [_jsx(PageHeader, { title: t("response_letters.title"), subtitle: t("response_letters.subtitle") }), _jsx(Card, { title: t("response_letters.manage"), children: _jsxs("div", { className: "flex gap-3", children: [_jsx("input", { type: "number", placeholder: t("response_letters.manuscript_id_placeholder"), value: manuscriptId, onChange: (e) => setManuscriptId(e.target.value), className: "flex-1 px-3 py-2 text-sm bg-surface border border-border rounded-lg text-text placeholder-text-faint focus:border-primary focus:ring-1 focus:ring-primary" }), _jsx(Button, { onClick: () => loadLetters(), disabled: !manuscriptId, children: t("response_letters.load") }), _jsxs(Button, { variant: "secondary", onClick: handleGenerate, disabled: generating || !manuscriptId, children: [generating && _jsx(Loader2, { className: "w-4 h-4 animate-spin" }), _jsx(Plus, { className: "w-4 h-4" }), t("response_letters.generate")] })] }) }), letters.length === 0 ? (_jsx(Card, { children: _jsx(EmptyState, { icon: _jsx(FileText, { className: "w-10 h-10" }), title: t("response_letters.no_letters"), description: t("response_letters.no_letters_desc") }) })) : (_jsx("div", { className: "space-y-4", children: letters.map((letter) => (_jsx("div", { className: "bg-surface border border-border rounded-xl shadow-sm hover:border-primary/30 transition-colors cursor-pointer", onClick: () => setSelectedLetter(letter), children: _jsxs("div", { className: "flex items-center justify-between gap-4 px-5 py-4", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "w-10 h-10 rounded-lg bg-info-subtle flex items-center justify-center", children: _jsx(FileText, { className: "w-5 h-5 text-info" }) }), _jsxs("div", { children: [_jsxs("p", { className: "font-medium text-text", children: [t("response_letters.letter"), " #", letter.id] }), _jsx("p", { className: "text-sm text-text-muted", children: new Date(letter.created_at).toLocaleDateString() })] })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx(Badge, { variant: "info", children: t("response_letters.generated") }), _jsx(Eye, { className: "w-4 h-4 text-text-faint" })] })] }) }, letter.id))) })), _jsx(Modal, { open: !!selectedLetter, onClose: () => setSelectedLetter(null), title: t("response_letters.view"), footer: _jsxs("div", { className: "flex gap-2", children: [_jsx(Button, { variant: "ghost", onClick: () => setSelectedLetter(null), children: t("common.close") }), _jsxs(Button, { variant: "secondary", children: [_jsx(RefreshCw, { className: "w-4 h-4" }), t("response_letters.regenerate")] })] }), children: selectedLetter && (_jsxs("div", { className: "space-y-4 max-h-96 overflow-y-auto", children: [selectedLetter.cover_letter && (_jsxs("div", { children: [_jsx("h4", { className: "font-medium text-text mb-2", children: t("response_letters.cover_letter") }), _jsx("div", { className: "p-4 bg-surface-2 rounded-lg text-sm text-text whitespace-pre-wrap", children: selectedLetter.cover_letter })] })), selectedLetter.response_body && (_jsxs("div", { children: [_jsx("h4", { className: "font-medium text-text mb-2", children: t("response_letters.response_body") }), _jsx("div", { className: "p-4 bg-surface-2 rounded-lg text-sm text-text whitespace-pre-wrap", children: selectedLetter.response_body })] })), !selectedLetter.cover_letter && !selectedLetter.response_body && (_jsx("p", { className: "text-text-muted text-sm", children: t("response_letters.no_content") }))] })) })] }));
}
