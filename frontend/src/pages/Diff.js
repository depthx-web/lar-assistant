import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState } from "react";
import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { EmptyState } from "../components/ui/EmptyState";
import { Loader2, GitCompare } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../components/ui/Toast";
import api from "../lib/api";
export default function DiffPage() {
    const { t } = useI18n();
    const { addToast } = useToast();
    const [manuscriptId, setManuscriptId] = useState("");
    const [versionFrom, setVersionFrom] = useState("");
    const [versionTo, setVersionTo] = useState("");
    const [diff, setDiff] = useState(null);
    const [loading, setLoading] = useState(false);
    const handleCompare = async () => {
        if (!manuscriptId || !versionFrom || !versionTo) {
            addToast({ variant: "warning", title: t("common.required") });
            return;
        }
        setLoading(true);
        try {
            const res = await api.get(`/manuscripts/${manuscriptId}/diff`, { params: { from_version: Number(versionFrom), to_version: Number(versionTo) } });
            setDiff(res.data);
        }
        catch {
            addToast({ variant: "error", title: t("common.error") });
        }
        finally {
            setLoading(false);
        }
    };
    return (_jsxs("div", { className: "space-y-6 max-w-5xl", children: [_jsx(PageHeader, { title: t("diff.title"), subtitle: t("diff.subtitle") }), _jsxs(Card, { title: t("diff.compare"), children: [_jsxs("div", { className: "grid grid-cols-3 gap-3", children: [_jsx(Input, { type: "number", placeholder: t("diff.version_from"), value: versionFrom, onChange: (e) => setVersionFrom(e.target.value) }), _jsx(Input, { type: "number", placeholder: t("diff.version_to"), value: versionTo, onChange: (e) => setVersionTo(e.target.value) }), _jsxs(Button, { onClick: handleCompare, disabled: loading || !manuscriptId || !versionFrom || !versionTo, children: [loading && _jsx(Loader2, { className: "w-4 h-4 animate-spin" }), t("diff.compare")] })] }), _jsx(Input, { type: "number", placeholder: t("manuscripts.select"), value: manuscriptId, onChange: (e) => setManuscriptId(e.target.value), className: "mt-3" })] }), loading && (_jsx(Card, { children: _jsxs("div", { className: "flex items-center justify-center py-12", children: [_jsx(Loader2, { className: "w-8 h-8 animate-spin text-text-faint" }), _jsx("span", { className: "ml-3 text-text-muted", children: t("diff.loading_diff") })] }) })), diff && (_jsxs(_Fragment, { children: [_jsxs("div", { className: "grid grid-cols-4 gap-4", children: [_jsxs(Card, { className: "text-center", children: [_jsx("p", { className: "text-2xl font-semibold text-success", children: diff.additions }), _jsx("p", { className: "text-xs text-text-muted", children: t("diff.additions") })] }), _jsxs(Card, { className: "text-center", children: [_jsx("p", { className: "text-2xl font-semibold text-error", children: diff.deletions }), _jsx("p", { className: "text-xs text-text-muted", children: t("diff.deletions") })] }), _jsxs(Card, { className: "text-center", children: [_jsx("p", { className: "text-2xl font-semibold text-text", children: diff.hunks_count }), _jsx("p", { className: "text-xs text-text-muted", children: t("tags_comments.version") })] }), _jsxs(Card, { className: "text-center", children: [_jsx("p", { className: "text-2xl font-semibold text-text", children: diff.summary?.net_change || 0 }), _jsx("p", { className: "text-xs text-text-muted", children: t("diff.lines_changed") })] })] }), _jsx(Card, { title: t("diff.compare"), children: diff.hunks.length === 0 ? (_jsx(EmptyState, { icon: _jsx(GitCompare, { className: "w-10 h-10" }), title: t("diff.no_diff"), description: t("diff.no_diff_desc") })) : (_jsx("div", { className: "space-y-3 font-mono text-sm", children: diff.hunks.map((hunk, i) => (_jsxs("div", { className: "border border-border rounded-lg overflow-hidden", children: [_jsxs("div", { className: "bg-surface-2 px-3 py-2 text-xs text-text-muted", children: ["@@ -", hunk.old_start, ",+", hunk.new_start, " @@"] }), _jsxs("div", { className: "p-3", children: [hunk.old_lines?.map((line, j) => (_jsx("div", { className: `${hunk.op === "delete" ? "bg-error-subtle text-error" : "text-text"} px-2`, children: line }, j))), hunk.new_lines?.map((line, j) => (_jsx("div", { className: `${hunk.op === "add" ? "bg-success-subtle text-success" : "text-text"} px-2`, children: line }, j)))] })] }, i))) })) })] }))] }));
}
