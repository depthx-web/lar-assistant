import { useState, useEffect } from "react";
import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { Progress } from "../components/ui/Progress";
import { EmptyState } from "../components/ui/EmptyState";
import { Modal } from "../components/ui/Modal";
import { Alert } from "../components/ui/Alert";
import { FileText, Star, Loader2, ChevronRight, CheckCircle2, XCircle } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../components/ui/Toast";
import api from "../lib/api";

interface Evaluation {
  id: number;
  manuscript_version_id: number;
  journal_id?: number;
  status: string;
  scores?: Record<string, number>;
  final_status?: string;
  model?: string;
  created_at: string;
}

export default function EvaluationsPage() {
  const { t } = useI18n();
  const { addToast } = useToast();
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEval, setSelectedEval] = useState<Evaluation | null>(null);

  useEffect(() => {
    loadEvaluations();
  }, []);

  const loadEvaluations = async () => {
    try {
      const msRes = await api.get("/manuscripts?limit=20");
      const manuscripts = msRes.data.manuscripts || [];
      const evalPromises = manuscripts.map(async (ms: { id: number; analysis_status: string; title: string }) => {
        if (ms.analysis_status === "COMPLETED") return null;
        try {
          const res = await api.post(`/manuscripts/${ms.id}/evaluate`, { model: "qwen2.5:3b-instruct" });
          return res.data;
        } catch { return null; }
      });
      const results = await Promise.all(evalPromises);
      setEvaluations(results.filter(Boolean));
    } catch {
      // Silently handle error
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score?: number) => {
    if (!score) return "text-text-muted";
    if (score >= 80) return "text-success";
    if (score >= 60) return "text-warning";
    return "text-error";
  };

  if (loading) {
    return (
      <div className="space-y-6 max-w-5xl">
        <PageHeader title={t("evaluations.title")} subtitle={t("evaluations.subtitle")} />
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
      <PageHeader title={t("evaluations.title")} subtitle={t("evaluations.subtitle")} />

      {evaluations.length === 0 ? (
        <Card>
          <EmptyState
            icon={<Star className="w-10 h-10" />}
            title={t("evaluations.no_evaluations")}
            description={t("evaluations.no_evaluations_desc")}
          />
        </Card>
      ) : (
        <div className="space-y-4">
          {evaluations.map((evalItem) => (
            <div
              key={evalItem.id}
              className="bg-surface border border-border rounded-xl shadow-sm hover:border-primary/30 transition-colors cursor-pointer"
              onClick={() => setSelectedEval(evalItem)}
            >
              <div className="flex items-center justify-between gap-4 px-5 py-4">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${evalItem.final_status === "APPROVED" ? "bg-success-subtle" : evalItem.final_status === "REJECTED" ? "bg-error-subtle" : "bg-warning-subtle"}`}>
                    {evalItem.final_status === "APPROVED" ? <CheckCircle2 className="w-5 h-5 text-success" /> : evalItem.final_status === "REJECTED" ? <XCircle className="w-5 h-5 text-error" /> : <Star className="w-5 h-5 text-warning" />}
                  </div>
                  <div>
                    <p className="font-medium text-text">Evaluation #{evalItem.id}</p>
                    <p className="text-sm text-text-muted">{t("evaluations.journal")}: {evalItem.journal_id || "—"} • {new Date(evalItem.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  {evalItem.scores?.compliance_score != null && (
                    <div className="text-right">
                      <p className={`text-lg font-semibold ${getScoreColor(evalItem.scores.compliance_score)}`}>{evalItem.scores.compliance_score}%</p>
                      <p className="text-xs text-text-muted">{t("evaluations.compliance")}</p>
                    </div>
                  )}
                  <Badge variant={evalItem.final_status === "APPROVED" ? "success" : evalItem.final_status === "REJECTED" ? "error" : "warning"}>
                    {evalItem.final_status || evalItem.status}
                  </Badge>
                  <ChevronRight className="w-5 h-5 text-text-faint" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal
        open={!!selectedEval}
        onClose={() => setSelectedEval(null)}
        title={t("evaluations.detail")}
        footer={
          <Button variant="ghost" onClick={() => setSelectedEval(null)}>
            {t("common.close")}
          </Button>
        }
      >
        {selectedEval && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-text">{t("manuscripts.overall_score")}</span>
              <span className={`text-2xl font-bold ${getScoreColor(selectedEval.scores?.compliance_score)}`}>
                {selectedEval.scores?.compliance_score ?? "—"}%
              </span>
            </div>
            <Progress value={selectedEval.scores?.compliance_score || 0} showLabel />
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(selectedEval.scores || {}).map(([key, value]) => (
                <div key={key} className="p-3 bg-surface-2 rounded-lg">
                  <p className="text-xs text-text-muted capitalize">{key.replace(/_/g, " ")}</p>
                  <p className="text-lg font-semibold text-text mt-1">{value ?? "—"}</p>
                </div>
              ))}
            </div>
            <Alert variant={selectedEval.final_status === "APPROVED" ? "success" : selectedEval.final_status === "REJECTED" ? "error" : "warning"}>
              {selectedEval.final_status || selectedEval.status}
            </Alert>
          </div>
        )}
      </Modal>
    </div>
  );
}
