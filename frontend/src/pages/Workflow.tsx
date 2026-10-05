import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../lib/api";
import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Upload, Loader2, ArrowRight, FileText, CheckCircle2, Workflow } from "lucide-react";
import { useI18n } from "../context/I18nContext";

interface Manuscript { id: number; title: string; analysis_status?: string; overall_compliance_score?: number; }

export default function WorkflowPage() {
  const { t } = useI18n();
  const [manuscripts, setManuscripts] = useState<Manuscript[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/manuscripts?limit=20")
      .then((r) => { setManuscripts(r.data.manuscripts ?? []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const analyzedMs = manuscripts.filter((m) => m.analysis_status === "COMPLETED");

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-text-faint" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary/5 via-bg to-success/5 border border-border p-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl -translate-y-32 translate-x-32" />
        <div className="relative">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
              <Workflow className="w-5 h-5 text-primary-fg" />
            </div>
            <div>
              <PageHeader title={t("workflow.title")} subtitle={t("workflow.subtitle")} />
            </div>
          </div>
          <p className="text-text-muted max-w-xl mt-4">
            {t("workflow.add_document")}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Link to="/papers" className="group">
          <div className="glass-card bg-surface border border-border rounded-xl p-5 hover:border-primary/30 transition-all duration-200 hover-lift h-full">
            <div className="flex items-start justify-between mb-4">
              <div className="w-10 h-10 rounded-lg bg-primary-subtle flex items-center justify-center">
                <Upload className="w-5 h-5 text-primary" />
              </div>
              <ArrowRight className="w-4 h-4 text-text-faint group-hover:text-primary transition-colors" />
            </div>
            <h3 className="font-semibold text-text mb-1">{t("workflow.upload_paper")}</h3>
            <p className="text-sm text-text-muted">{t("workflow.add_document")}</p>
          </div>
        </Link>
        <Link to="/manuscripts" className="group">
          <div className="glass-card bg-surface border border-border rounded-xl p-5 hover:border-primary/30 transition-all duration-200 hover-lift h-full">
            <div className="flex items-start justify-between mb-4">
              <div className="w-10 h-10 rounded-lg bg-success-subtle flex items-center justify-center">
                <FileText className="w-5 h-5 text-success" />
              </div>
              <ArrowRight className="w-4 h-4 text-text-faint group-hover:text-success transition-colors" />
            </div>
            <h3 className="font-semibold text-text mb-1">{t("manuscripts.new")}</h3>
            <p className="text-sm text-text-muted">{t("manuscripts.new_desc")}</p>
          </div>
        </Link>
      </div>

      {analyzedMs.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-3">{t("nav.recent_analyses")}</h2>
          <div className="space-y-2">
            {analyzedMs.slice(0, 5).map((ms) => (
              <div key={ms.id} className="flex items-center justify-between p-4 bg-surface border border-border rounded-xl hover:border-primary/20 transition-all duration-200 hover-lift">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-8 h-8 rounded-lg bg-success-subtle flex items-center justify-center shrink-0">
                    <CheckCircle2 className="w-4 h-4 text-success" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-text truncate">{ms.title}</p>
                    <p className="text-xs text-text-muted">
                      Score: {ms.overall_compliance_score ?? '—'}%
                    </p>
                  </div>
                </div>
                <Link to="/response-letters">
                  <Button variant="ghost" size="sm">{t("response_letters.generate")}</Button>
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
