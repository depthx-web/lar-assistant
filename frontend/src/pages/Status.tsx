import { Card, PageHeader } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { Alert } from "../components/ui/Alert";
import api from "../lib/api";
import { useEffect, useState } from "react";
import { Activity, Database, HardDrive, Cpu, Loader2 } from "lucide-react";
import { useI18n } from "../context/I18nContext";

interface SystemStatusResponse { status: "ok" | "degraded"; components: Record<string, { name: string; status: "ok" | "error" | "unavailable"; detail?: string | null }>; uptime_check: boolean; }

export default function StatusPage() {
  const { t } = useI18n();
  const [data, setData] = useState<SystemStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // System status endpoint may not exist, gracefully handle 404
    api.get("/system/status")
      .then((r) => { setData(r.data); setLoading(false); })
      .catch(() => {
        // If endpoint doesn't exist, show info that it's unavailable
        setLoading(false);
        setError(null);
        // Set data to null - we'll show the "not configured" state
      });
  }, []);

  if (loading) {
    return (
      <div className="space-y-6 max-w-5xl">
        <PageHeader title={t("status.title")} subtitle={t("status.subtitle")} />
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-text-muted" />
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="space-y-6 max-w-5xl">
        <PageHeader title={t("status.title")} subtitle={t("status.subtitle")} />
        <Card className="text-center py-12">
          <div className="w-12 h-12 rounded-full bg-warning-subtle flex items-center justify-center mx-auto mb-3">
            <span className="text-xl">⚠</span>
          </div>
          <p className="text-sm font-medium text-text">{t("status.unavailable")}</p>
          <p className="text-xs text-text-muted mt-1">{t("status.system_status_desc")}</p>
        </Card>
      </div>
    );
  }

  const components = data?.components ?? {};
  const isHealthy = data?.status === "ok";

  const componentIcons: Record<string, React.ReactNode> = {
    database: <Database className="w-5 h-5" />,
    storage: <HardDrive className="w-5 h-5" />,
    ollama: <Cpu className="w-5 h-5" />,
    embedding: <Activity className="w-5 h-5" />,
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <PageHeader title={t("status.title")} subtitle={t("status.subtitle")} />

      <div className="grid grid-cols-2 gap-4">
        <Card className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            {isHealthy
              ? <span className="w-3 h-3 rounded-full bg-success" />
              : <span className="w-3 h-3 rounded-full bg-warning" />
            }
            <span className="text-lg font-semibold text-text capitalize">{data?.status || "unknown"}</span>
          </div>
          <p className="text-xs text-text-muted">{t("status.overall_status")}</p>
        </Card>
        <Card className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            {data?.uptime_check
              ? <span className="text-success">✓</span>
              : <span className="text-error">✗</span>
            }
            <span className="text-lg font-semibold text-text">{t("status.uptime_check")}</span>
          </div>
          <p className="text-xs text-text-muted">{t("status.service_connectivity")}</p>
        </Card>
      </div>

      <Card title={t("status.component_health")}>
        <div className="space-y-4">
          {Object.entries(components).map(([key, comp]) => (
            <div key={key} className="flex items-center justify-between py-2 border-b border-border last:border-0">
              <div className="flex items-center gap-3">
                <span className="text-text-muted">{componentIcons[key] || <Activity className="w-5 h-5" />}</span>
                <div>
                  <p className="text-sm font-medium text-text">{comp.name || key}</p>
                  {comp.detail && (
                    <p className="text-xs text-text-muted mt-0.5">{comp.detail}</p>
                  )}
                </div>
              </div>
              <Badge variant={comp.status === "ok" ? "success" : comp.status === "error" ? "error" : "warning"}>
                {comp.status}
              </Badge>
            </div>
          ))}
        </div>
      </Card>

      {!isHealthy && (
        <Alert variant="warning" title={t("status.system_degraded")}>
          {t("status.system_degraded_desc")}
        </Alert>
      )}
    </div>
  );
}
