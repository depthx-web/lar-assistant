import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { Skeleton } from "../components/ui/Skeleton";
import { EmptyState } from "../components/ui/EmptyState";
import { BookOpen, Loader2 } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../components/ui/Toast";
import api from "../lib/api";
import { useEffect, useState } from "react";
import { JournalInfo } from "../types";

export default function JournalsPage() {
  const { t } = useI18n();
  const { addToast } = useToast();
  const [journals, setJournals] = useState<JournalInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [loadingJournals, setLoadingJournals] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadJournals = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get("/journals?limit=100");
      setJournals(res.data.journals || []);
    } catch (err: any) {
      const msg = err.response?.data?.detail ?? t("common.error");
      setError(msg);
      setJournals([]);
    } finally {
      setLoading(false);
    }
  };

  const loadFromYaml = async () => {
    setLoadingJournals(true);
    try {
      await api.post("/journals/load");
      addToast({ variant: "success", title: t("journals.loaded") });
      loadJournals();
    } catch (err: any) {
      addToast({ variant: "error", title: t("common.error"), description: err.response?.data?.detail ?? t("journals.load_failed") });
    } finally {
      setLoadingJournals(false);
    }
  };

  const filtered = journals.filter(
    (j) =>
      j.name?.toLowerCase().includes(search.toLowerCase()) ||
      j.publisher?.toLowerCase().includes(search.toLowerCase()) ||
      j.slug?.toLowerCase().includes(search.toLowerCase())
  );

  const getScoreColor = (score?: number) => {
    if (!score) return "text-text-muted";
    if (score >= 80) return "text-success";
    if (score >= 60) return "text-warning";
    return "text-error";
  };

  return (
    <div className="space-y-6 max-w-6xl">
      <PageHeader
        title={t("journals.title")}
        subtitle={t("journals.subtitle", { count: journals.length })}
        action={
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm" onClick={loadJournals} disabled={loading}>
              {loading && <Loader2 className="w-4 h-4 animate-spin" />}
              {t("journals.refresh")}
            </Button>
            <Button variant="primary" size="sm" onClick={loadFromYaml} disabled={loadingJournals}>
              {loadingJournals && <Loader2 className="w-4 h-4 animate-spin" />}
              {t("journals.load")}
            </Button>
          </div>
        }
      />

      {error && (
        <div className="p-4 bg-error-subtle border border-error/20 rounded-lg text-sm text-error">
          {error}
        </div>
      )}

      <input
        type="text"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder={t("journals.search")}
        className="w-full px-4 py-2 text-sm bg-surface border border-border rounded-lg text-text placeholder-text-faint focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none"
      />

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-20" />)}
        </div>
      ) : filtered.length === 0 ? (
        <Card>
          <EmptyState
            icon={<BookOpen className="w-10 h-10" />}
            title={t("journals.no_journals")}
            description={t("journals.no_journals_desc")}
            action={
              <Button variant="primary" onClick={loadFromYaml} disabled={loadingJournals}>
                {loadingJournals && <Loader2 className="w-4 h-4 animate-spin" />}
                {t("journals.load")}
              </Button>
            }
          />
        </Card>
      ) : (
        <div className="space-y-3">
          {filtered.map((journal) => (
            <div
              key={journal.id}
              className="flex items-center gap-4 p-4 bg-surface border border-border rounded-lg hover:border-primary/30 transition-colors hover-lift"
            >
              <div className="w-10 h-10 rounded-lg bg-primary-subtle flex items-center justify-center shrink-0">
                <BookOpen className="w-5 h-5 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-text truncate">{journal.name}</p>
                <p className="text-xs text-text-muted mt-0.5">
                  {journal.publisher && <span className="mr-3">{journal.publisher}</span>}
                  {journal.issn && <span className="mr-3">ISSN: {journal.issn}</span>}
                  <span className="text-text-faint">#{journal.id}</span>
                </p>
              </div>
              {journal.scope && (
                <p className="text-xs text-text-muted max-w-xs truncate hidden sm:block">
                  {journal.scope}
                </p>
              )}
              {journal.author_guidelines_url && (
                <a
                  href={journal.author_guidelines_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-primary hover:underline shrink-0"
                >
                  {t("journals.guidelines")}
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
