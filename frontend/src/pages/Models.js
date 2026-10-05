import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Card, PageHeader } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { EmptyState } from "../components/ui/EmptyState";
import { Alert } from "../components/ui/Alert";
import api from "../lib/api";
import { useEffect, useState } from "react";
import { Cpu } from "lucide-react";
import { useI18n } from "../context/I18nContext";
const ROLE_LABELS = {
    general_chat: "nav.chat",
    literature_analysis: "models.lit_analysis",
    academic_writing: "models.acad_writing",
    summarization: "models.summarization",
    embeddings: "models.embeddings",
    classification: "models.classification",
    journal_evaluation: "models.journal_eval",
};
export default function ModelsPage() {
    const { t } = useI18n();
    const [roles, setRoles] = useState([]);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        api.get("/system/models/roles")
            .then((r) => { setRoles(r.data.assignments); setLoading(false); })
            .catch(() => setLoading(false));
    }, []);
    return (_jsxs("div", { className: "space-y-6 max-w-5xl", children: [_jsx(PageHeader, { title: t("models.title"), subtitle: t("models.subtitle") }), _jsx(Alert, { variant: "info", title: t("models.model_roles"), children: t("models.model_roles_desc") }), _jsx(Card, { title: t("models.role_assignments"), children: loading ? (_jsx("div", { className: "space-y-2", children: [1, 2, 3].map((i) => _jsx("div", { className: "h-10 bg-surface-2 rounded animate-pulse" }, i)) })) : roles.length === 0 ? (_jsx(EmptyState, { icon: _jsx(Cpu, { className: "w-10 h-10" }), title: t("models.no_models"), description: t("models.no_models_desc"), action: _jsx(Button, { variant: "secondary", children: t("models.configure_models") }) })) : (_jsx("div", { className: "space-y-3", children: roles.map((role) => (_jsxs("div", { className: "flex items-center justify-between p-3 bg-surface-2 rounded-lg", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm font-medium text-text", children: t(ROLE_LABELS[role.role] || role.role) }), _jsx("p", { className: "text-xs text-text-muted", children: role.model_name ? `${role.model_name} (${role.provider})` : t("models.unassigned") })] }), _jsx(Badge, { variant: role.model_name ? "success" : "warning", children: role.model_name ? t("models.assigned") : t("models.unassigned") })] }, role.role))) })) }), _jsx(Card, { title: t("models.system_models"), children: _jsx(EmptyState, { title: t("models.backend_config"), description: t("models.backend_config_desc") }) })] }));
}
