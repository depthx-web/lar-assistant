import { useState, useEffect } from "react";
import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { Input } from "../components/ui/Input";
import { EmptyState } from "../components/ui/EmptyState";
import { Loader2, GitCompare } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../components/ui/Toast";
import api from "../lib/api";

interface DiffResult {
  additions: number;
  deletions: number;
  hunks_count: number;
  summary: {
    line_changes: { additions: number; deletions: number };
    total_old_lines: number;
    total_new_lines: number;
    net_change: number;
  };
  hunks: Array<{
    op: string;
    old_start: number;
    new_start: number;
    old_lines: string[];
    new_lines?: string[];
  }>;
}

export default function DiffPage() {
  const { t } = useI18n();
  const { addToast } = useToast();
  const [manuscriptId, setManuscriptId] = useState("");
  const [versionFrom, setVersionFrom] = useState("");
  const [versionTo, setVersionTo] = useState("");
  const [diff, setDiff] = useState<DiffResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleCompare = async () => {
    if (!manuscriptId || !versionFrom || !versionTo) {
      addToast({ variant: "warning", title: t("common.required") });
      return;
    }
    setLoading(true);
    try {
      const res = await api.get(`/manuscripts/${manuscriptId}/diff`, { params: { from_version: Number(versionFrom), to_version: Number(versionTo) } });
      setDiff(res.data);
    } catch {
      addToast({ variant: "error", title: t("common.error") });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <PageHeader title={t("diff.title")} subtitle={t("diff.subtitle")} />

      <Card title={t("diff.compare")}>
        <div className="grid grid-cols-3 gap-3">
          <Input
            type="number"
            placeholder={t("diff.version_from")}
            value={versionFrom}
            onChange={(e) => setVersionFrom(e.target.value)}
          />
          <Input
            type="number"
            placeholder={t("diff.version_to")}
            value={versionTo}
            onChange={(e) => setVersionTo(e.target.value)}
          />
          <Button onClick={handleCompare} disabled={loading || !manuscriptId || !versionFrom || !versionTo}>
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            {t("diff.compare")}
          </Button>
        </div>
        <Input
          type="number"
          placeholder={t("manuscripts.select")}
          value={manuscriptId}
          onChange={(e) => setManuscriptId(e.target.value)}
          className="mt-3"
        />
      </Card>

      {loading && (
        <Card>
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-text-faint" />
            <span className="ml-3 text-text-muted">{t("diff.loading_diff")}</span>
          </div>
        </Card>
      )}

      {diff && (
        <>
          <div className="grid grid-cols-4 gap-4">
            <Card className="text-center">
              <p className="text-2xl font-semibold text-success">{diff.additions}</p>
              <p className="text-xs text-text-muted">{t("diff.additions")}</p>
            </Card>
            <Card className="text-center">
              <p className="text-2xl font-semibold text-error">{diff.deletions}</p>
              <p className="text-xs text-text-muted">{t("diff.deletions")}</p>
            </Card>
            <Card className="text-center">
              <p className="text-2xl font-semibold text-text">{diff.hunks_count}</p>
              <p className="text-xs text-text-muted">{t("tags_comments.version")}</p>
            </Card>
            <Card className="text-center">
              <p className="text-2xl font-semibold text-text">{diff.summary?.net_change || 0}</p>
              <p className="text-xs text-text-muted">{t("diff.lines_changed")}</p>
            </Card>
          </div>

          <Card title={t("diff.compare")}>
            {diff.hunks.length === 0 ? (
              <EmptyState
                icon={<GitCompare className="w-10 h-10" />}
                title={t("diff.no_diff")}
                description={t("diff.no_diff_desc")}
              />
            ) : (
              <div className="space-y-3 font-mono text-sm">
                {diff.hunks.map((hunk, i) => (
                  <div key={i} className="border border-border rounded-lg overflow-hidden">
                    <div className="bg-surface-2 px-3 py-2 text-xs text-text-muted">
                      @@ -{hunk.old_start},+{hunk.new_start} @@
                    </div>
                    <div className="p-3">
                      {hunk.old_lines?.map((line, j) => (
                        <div key={j} className={`${hunk.op === "delete" ? "bg-error-subtle text-error" : "text-text"} px-2`}>{line}</div>
                      ))}
                      {hunk.new_lines?.map((line, j) => (
                        <div key={j} className={`${hunk.op === "add" ? "bg-success-subtle text-success" : "text-text"} px-2`}>{line}</div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </>
      )}
    </div>
  );
}


