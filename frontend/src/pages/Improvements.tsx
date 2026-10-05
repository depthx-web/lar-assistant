import { useState, useEffect } from "react";
import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { EmptyState } from "../components/ui/EmptyState";
import { Modal } from "../components/ui/Modal";
import { Loader2, Lightbulb, CheckCircle2 } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../components/ui/Toast";
import api from "../lib/api";

interface Improvement {
  id: number;
  manuscript_id: number;
  suggestion_type: string;
  severity: string;
  description: string;
  suggested_fix?: string;
  status: string;
  created_at: string;
}

export default function ImprovementsPage() {
  const { t } = useI18n();
  const { addToast } = useToast();
  const [manuscriptId, setManuscriptId] = useState("");
  const [suggestions, setSuggestions] = useState<Improvement[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState<Improvement | null>(null);

  const loadSuggestions = async () => {
    if (!manuscriptId) return;
    setLoading(true);
    try {
      const res = await api.get(`/manuscripts/${manuscriptId}/improvements`);
      setSuggestions(res.data.suggestions || []);
    } catch {
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!manuscriptId) return;
    setGenerating(true);
    try {
      const res = await api.post(`/manuscripts/${manuscriptId}/improvements/generate`, {
        evaluation_id: null,
        force_regenerate: false,
      });
      setSuggestions(res.data.suggestions || []);
      addToast({ variant: "success", title: t("common.saved") });
    } catch (err: any) {
      addToast({
        variant: "error",
        title: t("common.error"),
        description: err.response?.data?.detail || t("common.error"),
      });
    } finally {
      setGenerating(false);
    }
  };

  const handleAddress = async (suggestionId: number) => {
    try {
      await api.post(`/manuscripts/${manuscriptId}/improvements/${suggestionId}/address`, {
        version_id: null,
        reviewer: "user",
      });
      loadSuggestions();
      setSelectedSuggestion(null);
      addToast({ variant: "success", title: t("common.saved") });
    } catch {
      addToast({ variant: "error", title: t("common.error") });
    }
  };

  const addressedCount = suggestions.filter((s) => s.status === "ADDRESSED").length;
  const pendingCount = suggestions.filter((s) => s.status !== "ADDRESSED").length;

  return (
    <div className="space-y-6 max-w-5xl">
      <PageHeader title={t("improvements.title")} subtitle={t("improvements.subtitle")} />

      <Card title={t("manuscripts.select")}>
        <div className="flex gap-3">
          <input
            type="number"
            placeholder={t("manuscripts.select")}
            value={manuscriptId}
            onChange={(e) => setManuscriptId(e.target.value)}
            className="flex-1 px-3 py-2 text-sm bg-surface border border-border rounded-lg text-text placeholder-text-faint focus:border-primary focus:ring-1 focus:ring-primary"
          />
          <Button onClick={loadSuggestions} disabled={!manuscriptId || loading}>
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            {t("journals.load")}
          </Button>
          <Button variant="secondary" onClick={handleGenerate} disabled={generating || !manuscriptId}>
            {generating && <Loader2 className="w-4 h-4 animate-spin" />}
            <Lightbulb className="w-4 h-4" />
            {t("improvements.generate")}
          </Button>
        </div>
      </Card>

      {suggestions.length > 0 && (
        <div className="grid grid-cols-3 gap-4">
          <Card className="text-center">
            <p className="text-3xl font-semibold text-text">{suggestions.length}</p>
            <p className="text-xs text-text-muted mt-1">{t("improvements.total")}</p>
          </Card>
          <Card className="text-center border-success">
            <p className="text-3xl font-semibold text-success">{addressedCount}</p>
            <p className="text-xs text-text-muted mt-1">{t("improvements.addressed_count")}</p>
          </Card>
          <Card className="text-center border-warning">
            <p className="text-3xl font-semibold text-warning">{pendingCount}</p>
            <p className="text-xs text-text-muted mt-1">{t("improvements.pending_count")}</p>
          </Card>
        </div>
      )}

      {loading ? (
        <Card>
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-text-faint" />
          </div>
        </Card>
      ) : suggestions.length === 0 ? (
        <Card>
          <EmptyState
            icon={<Lightbulb className="w-10 h-10" />}
            title={t("improvements.no_suggestions")}
            description={t("improvements.no_suggestions_desc")}
          />
        </Card>
      ) : (
        <div className="space-y-3">
          {suggestions.map((s) => (
            <div
              key={s.id}
              className="bg-surface border border-border rounded-xl shadow-sm hover:border-primary/30 transition-colors cursor-pointer"
              onClick={() => setSelectedSuggestion(s)}
            >
              <div className="flex items-center justify-between gap-4 px-5 py-4">
                <div className="flex items-center gap-3">
                  <Badge variant={
                    s.severity === "critical" ? "error" :
                    s.severity === "warning" ? "warning" : "info"
                  }>
                    {s.severity}
                  </Badge>
                  <span className="text-sm text-text-muted capitalize">{s.suggestion_type}</span>
                  <p className="text-sm text-text">{s.description}</p>
                </div>
                <Badge variant={s.status === "ADDRESSED" ? "success" : "warning"}>
                  {s.status === "ADDRESSED" ? t("improvements.addressed") : t("improvements.pending")}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal
        open={!!selectedSuggestion}
        onClose={() => setSelectedSuggestion(null)}
        title={`${t("tags_comments.comment_text")}: ${selectedSuggestion?.id}`}
        footer={
          <div className="flex gap-2">
            <Button variant="ghost" onClick={() => setSelectedSuggestion(null)}>{t("common.close")}</Button>
            {selectedSuggestion?.status !== "ADDRESSED" && (
              <Button onClick={() => selectedSuggestion && handleAddress(selectedSuggestion.id)}>
                <CheckCircle2 className="w-4 h-4" />
                {t("improvements.address")}
              </Button>
            )}
          </div>
        }
      >
        {selectedSuggestion && (
          <div className="space-y-4">
            <div className="flex gap-2">
              <Badge variant={selectedSuggestion.severity === "critical" ? "error" : selectedSuggestion.severity === "warning" ? "warning" : "info"}>
                {selectedSuggestion.severity}
              </Badge>
              <Badge variant="info">{selectedSuggestion.suggestion_type}</Badge>
              <Badge variant={selectedSuggestion.status === "ADDRESSED" ? "success" : "warning"}>
                {selectedSuggestion.status}
              </Badge>
            </div>
            <p className="text-text">{selectedSuggestion.description}</p>
            {selectedSuggestion.suggested_fix && (
              <div className="p-4 bg-surface-2 rounded-lg">
                <p className="text-sm font-medium text-text mb-2">{t("tags_comments.comment_text")}</p>
                <p className="text-sm text-text-muted whitespace-pre-wrap">{selectedSuggestion.suggested_fix}</p>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
