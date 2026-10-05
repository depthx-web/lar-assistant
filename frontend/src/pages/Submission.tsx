import { useState, useEffect } from "react";
import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { Progress } from "../components/ui/Progress";
import { EmptyState } from "../components/ui/EmptyState";
import { Alert } from "../components/ui/Alert";
import { Input } from "../components/ui/Input";
import { Modal } from "../components/ui/Modal";
import { Loader2, Send, CheckCircle, XCircle } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../components/ui/Toast";
import api from "../lib/api";

export default function SubmissionPage() {
  const { t } = useI18n();
  const { addToast } = useToast();
  const [manuscriptId, setManuscriptId] = useState("");
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [changeSummary, setChangeSummary] = useState("");
  const [label, setLabel] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const loadStatus = async () => {
    if (!manuscriptId) return;
    setLoading(true);
    try {
      const res = await api.get(`/manuscripts/${manuscriptId}/submission/status`);
      setStatus(res.data);
    } catch {
      setStatus(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!manuscriptId) return;
    setSubmitting(true);
    try {
      await api.post(`/manuscripts/${manuscriptId}/submission`, {
        change_summary: changeSummary,
        label: label || undefined,
      });
      setShowSubmitModal(false);
      setChangeSummary("");
      setLabel("");
      loadStatus();
      addToast({ variant: "success", title: t("common.saved") });
    } catch {
      addToast({ variant: "error", title: t("common.error") });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <PageHeader title={t("submission.title")} subtitle={t("submission.subtitle")} />

      <Card title={t("manuscripts.select")}>
        <div className="flex gap-3">
          <Input
            type="number"
            placeholder={t("manuscripts.select")}
            value={manuscriptId}
            onChange={(e) => setManuscriptId(e.target.value)}
            className="flex-1"
          />
          <Button onClick={loadStatus} disabled={!manuscriptId || loading}>
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            {t("journals.load")}
          </Button>
        </div>
      </Card>

      {status && (
        <>
          <div className="grid grid-cols-2 gap-4">
            <Card className={status.ready_to_submit ? "border-success" : ""}>
              <div className="flex items-center gap-3">
                {status.ready_to_submit ? (
                  <CheckCircle className="w-8 h-8 text-success" />
                ) : (
                  <XCircle className="w-8 h-8 text-error" />
                )}
                <div>
                  <p className="font-semibold text-text">{status.ready_to_submit ? t("submission.ready_to_submit") : t("submission.not_ready")}</p>
                  <p className="text-sm text-text-muted">{status.ready_to_submit ? t("submission.ready_desc") : t("submission.not_ready_desc")}</p>
                </div>
              </div>
            </Card>
            {status.submitted_at && (
              <Card>
                <div className="flex items-center gap-3">
                  <Send className="w-8 h-8 text-info" />
                  <div>
                    <p className="font-semibold text-text">{t("submission.already_submitted")}</p>
                    <p className="text-sm text-text-muted">{new Date(status.submitted_at).toLocaleString()}</p>
                  </div>
                </div>
              </Card>
            )}
          </div>

          <Card title={t("submission.checklist")}>
            <div className="space-y-3">
              {[
                { key: "compliance_check", label: t("submission.compliance_check"), status: status.compliance_check },
                { key: "improvements_addressed", label: t("submission.improvements_addressed"), status: status.improvements_addressed },
                { key: "response_letters", label: t("submission.response_letters"), status: status.response_letters },
                { key: "export_ready", label: t("submission.export_ready"), status: status.export_ready },
              ].map((item) => (
                <div key={item.key} className="flex items-center justify-between p-3 bg-surface-2 rounded-lg">
                  <span className="text-sm text-text">{item.label}</span>
                  <Badge variant={item.status ? "success" : "muted"}>
                    {item.status ? t("common.saved") : t("submission.not_ready")}
                  </Badge>
                </div>
              ))}
            </div>
          </Card>

          {!status.submitted_at && status.ready_to_submit && (
            <Button size="lg" onClick={() => setShowSubmitModal(true)}>
              <Send className="w-5 h-5" />
              {t("submission.submit")}
            </Button>
          )}
        </>
      )}

      <Modal
        open={showSubmitModal}
        onClose={() => setShowSubmitModal(false)}
        title={t("submission.submit")}
        footer={
          <>
            <Button variant="ghost" onClick={() => setShowSubmitModal(false)}>{t("common.cancel")}</Button>
            <Button onClick={handleSubmit} disabled={submitting}>
              {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
              {t("submission.submit")}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label={t("submission.change_summary")}
            value={changeSummary}
            onChange={(e) => setChangeSummary(e.target.value)}
            placeholder={t("submission.change_summary_placeholder")}
          />
          <Input
            label={t("submission.label")}
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            placeholder={t("submission.label_placeholder")}
          />
        </div>
      </Modal>
    </div>
  );
}
