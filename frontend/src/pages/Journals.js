import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Skeleton } from "../components/ui/Skeleton";
import { EmptyState } from "../components/ui/EmptyState";
import { BookOpen, Loader2 } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../components/ui/Toast";
import api from "../lib/api";
import { useState } from "react";
export default function JournalsPage() {
    const { t } = useI18n();
    const { addToast } = useToast();
    const [journals, setJournals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [loadingJournals, setLoadingJournals] = useState(false);
    const [error, setError] = useState(null);
    const loadJournals = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await api.get("/journals?limit=100");
            setJournals(res.data.journals || []);
        }
        catch (err) {
            const msg = err.response?.data?.detail ?? t("common.error");
            setError(msg);
            setJournals([]);
        }
        finally {
            setLoading(false);
        }
    };
    const loadFromYaml = async () => {
        setLoadingJournals(true);
        try {
            await api.post("/journals/load");
            addToast({ variant: "success", title: t("journals.loaded") });
            loadJournals();
        }
        catch (err) {
            addToast({ variant: "error", title: t("common.error"), description: err.response?.data?.detail ?? t("journals.load_failed") });
        }
        finally {
            setLoadingJournals(false);
        }
    };
    const filtered = journals.filter((j) => j.name?.toLowerCase().includes(search.toLowerCase()) ||
        j.publisher?.toLowerCase().includes(search.toLowerCase()) ||
        j.slug?.toLowerCase().includes(search.toLowerCase()));
    const getScoreColor = (score) => {
        if (!score)
            return "text-text-muted";
        if (score >= 80)
            return "text-success";
        if (score >= 60)
            return "text-warning";
        return "text-error";
    };
    return (_jsxs("div", { className: "space-y-6 max-w-6xl", children: [_jsx(PageHeader, { title: t("journals.title"), subtitle: t("journals.subtitle", { count: journals.length }), action: _jsxs("div", { className: "flex items-center gap-2", children: [_jsxs(Button, { variant: "secondary", size: "sm", onClick: loadJournals, disabled: loading, children: [loading && _jsx(Loader2, { className: "w-4 h-4 animate-spin" }), t("journals.refresh")] }), _jsxs(Button, { variant: "primary", size: "sm", onClick: loadFromYaml, disabled: loadingJournals, children: [loadingJournals && _jsx(Loader2, { className: "w-4 h-4 animate-spin" }), t("journals.load")] })] }) }), error && (_jsx("div", { className: "p-4 bg-error-subtle border border-error/20 rounded-lg text-sm text-error", children: error })), _jsx("input", { type: "text", value: search, onChange: (e) => setSearch(e.target.value), placeholder: t("journals.search"), className: "w-full px-4 py-2 text-sm bg-surface border border-border rounded-lg text-text placeholder-text-faint focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none" }), loading ? (_jsx("div", { className: "space-y-3", children: [1, 2, 3, 4].map((i) => _jsx(Skeleton, { className: "h-20" }, i)) })) : filtered.length === 0 ? (_jsx(Card, { children: _jsx(EmptyState, { icon: _jsx(BookOpen, { className: "w-10 h-10" }), title: t("journals.no_journals"), description: t("journals.no_journals_desc"), action: _jsxs(Button, { variant: "primary", onClick: loadFromYaml, disabled: loadingJournals, children: [loadingJournals && _jsx(Loader2, { className: "w-4 h-4 animate-spin" }), t("journals.load")] }) }) })) : (_jsx("div", { className: "space-y-3", children: filtered.map((journal) => (_jsxs("div", { className: "flex items-center gap-4 p-4 bg-surface border border-border rounded-lg hover:border-primary/30 transition-colors hover-lift", children: [_jsx("div", { className: "w-10 h-10 rounded-lg bg-primary-subtle flex items-center justify-center shrink-0", children: _jsx(BookOpen, { className: "w-5 h-5 text-primary" }) }), _jsxs("div", { className: "flex-1 min-w-0", children: [_jsx("p", { className: "font-medium text-text truncate", children: journal.name }), _jsxs("p", { className: "text-xs text-text-muted mt-0.5", children: [journal.publisher && _jsx("span", { className: "mr-3", children: journal.publisher }), journal.issn && _jsxs("span", { className: "mr-3", children: ["ISSN: ", journal.issn] }), _jsxs("span", { className: "text-text-faint", children: ["#", journal.id] })] })] }), journal.scope && (_jsx("p", { className: "text-xs text-text-muted max-w-xs truncate hidden sm:block", children: journal.scope })), journal.author_guidelines_url && (_jsx("a", { href: journal.author_guidelines_url, target: "_blank", rel: "noopener noreferrer", className: "text-xs text-primary hover:underline shrink-0", children: t("journals.guidelines") }))] }, journal.id))) }))] }));
}
