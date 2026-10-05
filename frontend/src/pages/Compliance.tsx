import { Card, PageHeader } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Skeleton } from "../components/ui/Skeleton";
import { EmptyState } from "../components/ui/EmptyState";
import { Alert } from "../components/ui/Alert";
import api from "../lib/api";
import { useEffect, useState } from "react";
import { FileText } from "lucide-react";
import { useI18n } from "../context/I18nContext";

interface QueueJob { id: number; job_type: string; status: string; progress: number; created_at: string; error?: string | null; }
interface QueueResponse { jobs: QueueJob[]; total: number; active: number; }

export default function CompliancePage() {
  const { t } = useI18n();
  const [queue, setQueue] = useState<QueueResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/system/queue")
      .then((r) => { setQueue(r.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6 max-w-5xl">
      <PageHeader title={t("compliance.title")} subtitle={t("compliance.subtitle")} />

      <div className="grid grid-cols-3 gap-4">
        <Card className="text-center">
          <p className="text-3xl font-semibold text-text">—</p>
          <p className="text-xs text-text-muted mt-1">{t("compliance.ready")}</p>
        </Card>
        <Card className="text-center">
          <p className="text-3xl font-semibold text-warning">—</p>
          <p className="text-xs text-text-muted mt-1">{t("compliance.needs_review")}</p>
        </Card>
        <Card className="text-center">
          <p className="text-3xl font-semibold text-success">—</p>
          <p className="text-xs text-text-muted mt-1">{t("compliance.submitted")}</p>
        </Card>
      </div>

      <Card title={t("compliance.processing_queue")}>
        {loading ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => <Skeleton key={i} className="h-10" />)}
          </div>
        ) : !queue || queue.jobs.length === 0 ? (
          <EmptyState
            icon={<FileText className="w-8 h-8 text-text-faint" />}
            title={t("compliance.queue_empty")}
            description={t("compliance.queue_empty_desc")}
          />
        ) : (
          <div className="space-y-2">
            {queue.jobs.map((job) => (
              <div key={job.id} className="flex items-center gap-4 p-3 bg-surface-2 rounded-lg">
                <span className="text-xs font-mono text-text-muted w-8">#{job.id}</span>
                <span className="text-sm font-medium text-text flex-1">{job.job_type}</span>
                <Badge variant={job.status === "SUCCEEDED" ? "success" : job.status === "FAILED" ? "error" : job.status === "RUNNING" ? "warning" : "muted"}>
                  {job.status}
                </Badge>
                <span className="text-xs text-text-faint">{new Date(job.created_at).toLocaleTimeString()}</span>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Alert variant="info" title={t("compliance.how_it_works")}>
        {t("compliance.how_it_works_desc")}
      </Alert>
    </div>
  );
}
