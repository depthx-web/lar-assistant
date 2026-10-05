import { useState, useEffect } from "react";
import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { EmptyState } from "../components/ui/EmptyState";
import { Modal } from "../components/ui/Modal";
import { FileText, Plus, Loader2, Eye, RefreshCw } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../components/ui/Toast";
import api from "../lib/api";

interface ResponseLetter {
  id: number;
  manuscript_id: number;
  evaluation_id?: number;
  cover_letter?: string;
  response_body?: string;
  created_at: string;
}

export default function ResponseLettersPage() {
  const { t } = useI18n();
  const { addToast } = useToast();
  const [letters, setLetters] = useState<ResponseLetter[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLetter, setSelectedLetter] = useState<ResponseLetter | null>(null);
  const [generating, setGenerating] = useState(false);
  const [manuscriptId, setManuscriptId] = useState("");

  useEffect(() => {
    if (manuscriptId) loadLetters();
  }, [manuscriptId]);

  const loadLetters = async () => {
    if (!manuscriptId) return;
    setLoading(true);
    try {
      const res = await api.get(`/manuscripts/${manuscriptId}/response-letters`);
      setLetters(res.data.letters || []);
    } catch {
      setLetters([]);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!manuscriptId) {
      addToast({ variant: "warning", title: t("response_letters.enter_manuscript") });
      return;
    }
    setGenerating(true);
    try {
      const res = await api.post(`/manuscripts/${manuscriptId}/response-letters/generate`, {});
      setLetters([res.data, ...letters]);
      addToast({ variant: "success", title: t("response_letters.generated") });
    } catch {
      addToast({ variant: "error", title: t("common.error"), description: t("response_letters.generate_failed") });
    } finally {
      setGenerating(false);
    }
  };

  if (loading && letters.length === 0) {
    return (
      <div className="space-y-6 max-w-5xl">
        <PageHeader title={t("response_letters.title")} subtitle={t("response_letters.subtitle")} />
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
      <PageHeader title={t("response_letters.title")} subtitle={t("response_letters.subtitle")} />

      <Card title={t("response_letters.manage")}>
        <div className="flex gap-3">
          <input
            type="number"
            placeholder={t("response_letters.manuscript_id_placeholder")}
            value={manuscriptId}
            onChange={(e) => setManuscriptId(e.target.value)}
            className="flex-1 px-3 py-2 text-sm bg-surface border border-border rounded-lg text-text placeholder-text-faint focus:border-primary focus:ring-1 focus:ring-primary"
          />
          <Button onClick={() => loadLetters()} disabled={!manuscriptId}>
            {t("response_letters.load")}
          </Button>
          <Button variant="secondary" onClick={handleGenerate} disabled={generating || !manuscriptId}>
            {generating && <Loader2 className="w-4 h-4 animate-spin" />}
            <Plus className="w-4 h-4" />
            {t("response_letters.generate")}
          </Button>
        </div>
      </Card>

      {letters.length === 0 ? (
        <Card>
          <EmptyState
            icon={<FileText className="w-10 h-10" />}
            title={t("response_letters.no_letters")}
            description={t("response_letters.no_letters_desc")}
          />
        </Card>
      ) : (
        <div className="space-y-4">
          {letters.map((letter) => (
            <div
              key={letter.id}
              className="bg-surface border border-border rounded-xl shadow-sm hover:border-primary/30 transition-colors cursor-pointer"
              onClick={() => setSelectedLetter(letter)}
            >
              <div className="flex items-center justify-between gap-4 px-5 py-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-info-subtle flex items-center justify-center">
                    <FileText className="w-5 h-5 text-info" />
                  </div>
                  <div>
                    <p className="font-medium text-text">{t("response_letters.letter")} #{letter.id}</p>
                    <p className="text-sm text-text-muted">{new Date(letter.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="info">{t("response_letters.generated")}</Badge>
                  <Eye className="w-4 h-4 text-text-faint" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal
        open={!!selectedLetter}
        onClose={() => setSelectedLetter(null)}
        title={t("response_letters.view")}
        footer={
          <div className="flex gap-2">
            <Button variant="ghost" onClick={() => setSelectedLetter(null)}>{t("common.close")}</Button>
            <Button variant="secondary">
              <RefreshCw className="w-4 h-4" />
              {t("response_letters.regenerate")}
            </Button>
          </div>
        }
      >
        {selectedLetter && (
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {selectedLetter.cover_letter && (
              <div>
                <h4 className="font-medium text-text mb-2">{t("response_letters.cover_letter")}</h4>
                <div className="p-4 bg-surface-2 rounded-lg text-sm text-text whitespace-pre-wrap">{selectedLetter.cover_letter}</div>
              </div>
            )}
            {selectedLetter.response_body && (
              <div>
                <h4 className="font-medium text-text mb-2">{t("response_letters.response_body")}</h4>
                <div className="p-4 bg-surface-2 rounded-lg text-sm text-text whitespace-pre-wrap">{selectedLetter.response_body}</div>
              </div>
            )}
            {!selectedLetter.cover_letter && !selectedLetter.response_body && (
              <p className="text-text-muted text-sm">{t("response_letters.no_content")}</p>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
