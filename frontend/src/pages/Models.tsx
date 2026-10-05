import { Card, PageHeader } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { EmptyState } from "../components/ui/EmptyState";
import { Alert } from "../components/ui/Alert";
import api from "../lib/api";
import { useEffect, useState } from "react";
import { Cpu } from "lucide-react";
import { useI18n } from "../context/I18nContext";

interface ModelRoleAssignment { role: string; model_name: string | null; provider: string | null; }
interface ModelRoleListResponse { assignments: ModelRoleAssignment[]; }

const ROLE_LABELS: Record<string, string> = {
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
  const [roles, setRoles] = useState<ModelRoleAssignment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/system/models/roles")
      .then((r) => { setRoles(r.data.assignments); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6 max-w-5xl">
      <PageHeader title={t("models.title")} subtitle={t("models.subtitle")} />

      <Alert variant="info" title={t("models.model_roles")}>
        {t("models.model_roles_desc")}
      </Alert>

      <Card title={t("models.role_assignments")}>
        {loading ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => <div key={i} className="h-10 bg-surface-2 rounded animate-pulse" />)}
          </div>
        ) : roles.length === 0 ? (
          <EmptyState
            icon={<Cpu className="w-10 h-10" />}
            title={t("models.no_models")}
            description={t("models.no_models_desc")}
            action={<Button variant="secondary">{t("models.configure_models")}</Button>}
          />
        ) : (
          <div className="space-y-3">
            {roles.map((role) => (
              <div key={role.role} className="flex items-center justify-between p-3 bg-surface-2 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-text">{t(ROLE_LABELS[role.role] || role.role)}</p>
                  <p className="text-xs text-text-muted">
                    {role.model_name ? `${role.model_name} (${role.provider})` : t("models.unassigned")}
                  </p>
                </div>
                <Badge variant={role.model_name ? "success" : "warning"}>
                  {role.model_name ? t("models.assigned") : t("models.unassigned")}
                </Badge>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Card title={t("models.system_models")}>
        <EmptyState
          title={t("models.backend_config")}
          description={t("models.backend_config_desc")}
        />
      </Card>
    </div>
  );
}
