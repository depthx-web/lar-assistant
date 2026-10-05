import { useState, useEffect } from "react";
import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { Progress } from "../components/ui/Progress";
import { EmptyState } from "../components/ui/EmptyState";
import { Loader2, Download, Plus } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../components/ui/Toast";
import api from "../lib/api";

interface ExportJob {
  id: number;
  manuscript_id: number;
  format: string;
  status: string;
  progress: number;
  created_at: string;
  error?: string | null;
}

const FORMATS = ["pdf", "docx", "markdown", "tex"];

export default function ExportsPage() {
  const { t } = useI18n();
  const { addToast } = useToast();
  const [manuscriptId, setManuscriptId] = useState("");
  const [exports, setExports] = useState<ExportJob[]>([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState("pdf");

  const loadExports = async () => {
    if (!manuscriptId) return;
    setLoading(true);
    try {
      const res = await api.get(`/manuscripts/${manuscriptId}/exports`);
      setExports(res.data.jobs || []);
    } catch {
      setExports([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!manuscriptId) return;
    setCreating(true);
    try {
      await api.post(`/manuscripts/${manuscriptId}/export`, { format: selectedFormat, version_id: null });
      addToast({ variant: "success", title: t("common.saved") });
      loadExports();
    } catch {
      addToast({ variant: "error", title: t("common.error") });
    } finally {
      setCreating(false);
    }
  };

  const handleRun = async (jobId: number) => {
    try {
      await api.post(`/manuscripts/${manuscriptId}/export/${jobId}/run`, {});
      loadExports();
    } catch {
      addToast({ variant: "error", title: t("common.error") });
    }
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <PageHeader title={t("exports.title")} subtitle={t("exports.subtitle")} />

      <Card title={t("exports.export")}>
        <div className="flex gap-3 items-end">
          <div className="flex-1">
            <label className="text-sm font-medium text-text mb-1 block">{t("manuscripts.select")}</label>
            <input
              type="number"
              value={manuscriptId}
              onChange={(e) => setManuscriptId(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-surface border border-border rounded-lg text-text placeholder-text-faint focus:border-primary focus:ring-1 focus:ring-primary"
          placeholder={t("manuscripts.select")}
            />
          </div>
          <div>
            <label className="text-sm font-medium text-text mb-1 block">{t("exports.export_format")}</label>
            <select
              value={selectedFormat}
              onChange={(e) => setSelectedFormat(e.target.value)}
              className="px-3 py-2 text-sm bg-surface border border-border rounded-lg text-text focus:border-primary focus:ring-1 focus:ring-primary"
            >
              {FORMATS.map((f) => <option key={f} value={f}>{f.toUpperCase()}</option>)}
            </select>
          </div>
          <Button onClick={handleCreate} disabled={creating || !manuscriptId}>
            {creating && <Loader2 className="w-4 h-4 animate-spin" />}
            <Plus className="w-4 h-4" />
            {t("exports.export")}
          </Button>
          <Button variant="secondary" onClick={loadExports} disabled={loading || !manuscriptId}>
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            {t("journals.load")}
          </Button>
        </div>
      </Card>

      {manuscriptId && !loading && exports.length === 0 ? (
        <Card>
          <EmptyState
            icon={<Download className="w-10 h-10" />}
            title={t("exports.no_exports")}
            description={t("exports.no_exports_desc")}
          />
        </Card>
      ) : (
        <div className="space-y-3">
          {exports.map((job) => (
            <div key={job.id} className="bg-surface border border-border rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <Badge variant="info">{job.format.toUpperCase()}</Badge>
                  <span className="text-sm text-text-muted">#{job.id}</span>
                </div>
                <Badge variant={
                  job.status === "COMPLETED" ? "success" :
                  job.status === "RUNNING" ? "warning" :
                  job.status === "FAILED" ? "error" : "muted"
                }>
                  {job.status}
                </Badge>
              </div>
              <Progress value={job.progress} className="mb-2" showLabel />
              <div className="flex justify-end gap-2">
                {job.status === "PENDING" && (
                  <Button size="sm" onClick={() => handleRun(job.id)}>{t("exports.run")}</Button>
                )}
                {job.status === "COMPLETED" && (
                  <Button size="sm" variant="secondary" onClick={() => addToast({ variant: "info", title: t("exports.download_started") })}>
                    <Download className="w-4 h-4" />
                    {t("exports.download")}
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
