import { useState, useEffect } from "react";
import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { Modal } from "../components/ui/Modal";
import { EmptyState } from "../components/ui/EmptyState";
import { Badge } from "../components/ui/Badge";
import { Progress } from "../components/ui/Progress";
import { ScrollText, Plus, Loader2, CheckCircle, XCircle, Play } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../components/ui/Toast";
import api from "../lib/api";

interface Manuscript {
  id: number;
  title: string;
  journal_id?: number;
  document_id?: number;
  analysis_status?: string;
  overall_compliance_score?: number;
  created_at: string;
}

export default function ManuscriptsPage() {
  const { t } = useI18n();
  const { addToast } = useToast();
  const [manuscripts, setManuscripts] = useState<Manuscript[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [journalId, setJournalId] = useState("");
  const [paperId, setPaperId] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [analyzingId, setAnalyzingId] = useState<number | null>(null);

  useEffect(() => {
    loadManuscripts();
  }, []);

  const loadManuscripts = async () => {
    try {
      const res = await api.get("/manuscripts");
      setManuscripts(res.data.manuscripts || []);
    } catch {
      // Silently handle error
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!title.trim()) {
      addToast({ variant: "warning", title: t("common.required") });
      return;
    }
    setSubmitting(true);
    try {
      await api.post("/manuscripts", {
        title: title.trim(),
        journal_id: journalId ? Number(journalId) : null,
        document_id: paperId ? Number(paperId) : null,
      });
      addToast({ variant: "success", title: t("manuscripts.created") });
      setModalOpen(false);
      setTitle("");
      setJournalId("");
      setPaperId("");
      loadManuscripts();
    } catch {
      addToast({ variant: "error", title: t("common.error"), description: t("manuscripts.create_failed") });
    } finally {
      setSubmitting(false);
    }
  };

  const handleAnalyze = async (id: number) => {
    setAnalyzingId(id);
    try {
      await api.post(`/manuscripts/${id}/analyze`);
      addToast({ variant: "success", title: t("manuscripts.analyzed") });
      loadManuscripts();
    } catch (err: any) {
      addToast({ variant: "error", title: t("common.error"), description: err.response?.data?.detail ?? "Analysis failed" });
    } finally {
      setAnalyzingId(null);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm(t("manuscripts.confirm_delete"))) return;
    try {
      await api.delete(`/manuscripts/${id}`);
      addToast({ variant: "success", title: t("manuscripts.deleted") });
      loadManuscripts();
    } catch {
      addToast({ variant: "error", title: t("common.error"), description: t("manuscripts.delete_failed") });
    }
  };

  if (loading) {
    return (
      <div className="space-y-6 max-w-5xl">
        <PageHeader title={t("manuscripts.title")} subtitle={t("manuscripts.subtitle")} />
        <Card>
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-text-faint" />
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl">
      <PageHeader
        title={t("manuscripts.title")}
        subtitle={t("manuscripts.subtitle")}
        action={
          <Button onClick={() => setModalOpen(true)}>
            <Plus className="w-4 h-4" />
            {t("manuscripts.new")}
          </Button>
        }
      />

      {manuscripts.length === 0 ? (
        <Card>
          <EmptyState
            icon={<ScrollText className="w-10 h-10" />}
            title={t("manuscripts.no_manuscripts")}
            description={t("manuscripts.no_manuscripts_desc")}
            action={
              <Button onClick={() => setModalOpen(true)}>
                <Plus className="w-4 h-4" />
                {t("manuscripts.new")}
              </Button>
            }
          />
        </Card>
      ) : (
        <div className="space-y-4">
          {manuscripts.map((ms) => (
            <Card key={ms.id} className="hover:border-primary/30 transition-colors">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <ScrollText className="w-4 h-4 text-text-faint" />
                    <h3 className="font-semibold text-text truncate">{ms.title}</h3>
                    <span className="text-xs text-text-faint">#{ms.id}</span>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-text-muted mt-2">
                    {ms.journal_id && (
                      <span>{t("manuscripts.journal")}: {ms.journal_id}</span>
                    )}
                    {ms.document_id && (
                      <span>{t("manuscripts.paper")}: {ms.document_id}</span>
                    )}
                    <span>{new Date(ms.created_at).toLocaleDateString()}</span>
                  </div>
                  {ms.overall_compliance_score != null && (
                    <div className="mt-3 flex items-center gap-3">
                      <Progress value={ms.overall_compliance_score ?? 0} size="sm" className="w-32" />
                      <span className={`text-sm font-medium ${ms.overall_compliance_score >= 80 ? "text-success" : ms.overall_compliance_score >= 60 ? "text-warning" : "text-error"}`}>
                        {Math.round(ms.overall_compliance_score * 100)}%
                      </span>
                      <Badge variant={ms.analysis_status === "COMPLETED" ? "success" : ms.analysis_status === "PROCESSING" ? "warning" : "muted"}>
                        {ms.analysis_status || "PENDING"}
                      </Badge>
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {ms.analysis_status !== "COMPLETED" && (
                    <Button variant="ghost" size="sm" onClick={() => handleAnalyze(ms.id)} title="Analyze manuscript" loading={analyzingId === ms.id}>
                      <Play className="w-4 h-4" />
                    </Button>
                  )}
                  <Button variant="ghost" size="sm" onClick={() => handleDelete(ms.id)} title={t("common.delete")} className="text-error hover:text-error">
                    <XCircle className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={t("manuscripts.new")}
        description={t("manuscripts.new_desc")}
        footer={
          <>
            <Button variant="ghost" onClick={() => setModalOpen(false)}>{t("common.cancel")}</Button>
            <Button onClick={handleCreate} disabled={submitting}>
              {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
              {t("manuscripts.create")}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input label={t("manuscripts.title")} value={title} onChange={(e) => setTitle(e.target.value)} placeholder={t("manuscripts.title_placeholder")} />
          <Input label={t("manuscripts.paper")} value={paperId} onChange={(e) => setPaperId(e.target.value)} placeholder={t("manuscripts.paper_placeholder")} helper={t("manuscripts.paper_helper")} />
          <Input label={t("manuscripts.journal")} value={journalId} onChange={(e) => setJournalId(e.target.value)} placeholder={t("manuscripts.journal_placeholder")} />
        </div>
      </Modal>
    </div>
  );
}
