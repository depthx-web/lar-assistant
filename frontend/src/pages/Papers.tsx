import { useEffect, useState } from "react";
import api from "../lib/api";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Skeleton } from "../components/ui/Skeleton";
import { DocumentMetadata } from "../types";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../components/ui/Toast";
import { useNavigate } from "react-router-dom";

export default function PapersPage() {
  const { t } = useI18n();
  const { addToast } = useToast();
  const navigate = useNavigate();
  const [docs, setDocs] = useState<DocumentMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const loadDocs = () => {
    setLoading(true);
    api.get("/documents")
      .then((r) => { setDocs(r.data.documents ?? []); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => { loadDocs(); }, []);

  const filtered = docs.filter(
    (d) =>
      d.title?.toLowerCase().includes(search.toLowerCase()) ||
      d.authors?.toLowerCase().includes(search.toLowerCase()) ||
      d.file_hash.toLowerCase().includes(search.toLowerCase())
  );

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadError(null);
    const form = new FormData();
    form.append("file", file);
    try {
      await api.post("/documents/upload", form, { headers: { "Content-Type": "multipart/form-data" } });
      addToast({ variant: "success", title: t("papers.upload_success"), description: file.name });
      loadDocs();
    } catch (err: any) {
      const msg = err.response?.data?.detail ?? t("common.error");
      setUploadError(msg);
      addToast({ variant: "error", title: t("papers.upload_failed"), description: msg });
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleProcess = async (id: number) => {
    try {
      await api.post(`/documents/${id}/process`);
      addToast({ variant: "success", title: t("papers.analyzed") });
      loadDocs();
    } catch (err: any) {
      addToast({ variant: "error", title: t("common.error"), description: err.response?.data?.detail ?? "Processing failed" });
    }
  };

  return (
    <div className="screen">
      <div className="pagehead">
        <div>
          <h1 className="t">{t("papers.title")}</h1>
          <p className="sub">{t("papers.documents_count", { count: docs.length })}</p>
        </div>
        <div className="actions">
          <label className="cursor-pointer">
            <input type="file" accept=".pdf,.docx,.txt" className="hidden" onChange={handleUpload} />
            <Button variant="secondary" size="sm" loading={uploading}>
              <svg className="i"><use href="#i-upload"/></svg>
              <span className="t">{t("papers.upload")}</span>
            </Button>
          </label>
          <Button variant="ghost" size="sm" onClick={loadDocs}>
            <svg className="i"><use href="#i-refresh"/></svg>
          </Button>
        </div>
      </div>

      {uploadError && (
        <div className="alert" role="alert">
          <svg className="i"><use href="#i-alert"/></svg>
          <div>
            <h3>{t("papers.upload_failed")}</h3>
            <p>{uploadError}</p>
          </div>
        </div>
      )}

      <div className="drop">
        <svg className="i"><use href="#i-upload"/></svg>
        <div>
          <b className="t">{t("papers.drop_files")}</b>
          <span className="t">{t("papers.drop_desc")}</span>
        </div>
      </div>

      <div className="toolbar">
        <input
          className="field srch"
          type="search"
          placeholder={t("papers.search_papers")}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className="chips" role="group">
          <button className="chip t" aria-pressed="true">{t("filters.all")}</button>
          <button className="chip t" aria-pressed="false">{t("filters.ready")}</button>
          <button className="chip t" aria-pressed="false">{t("filters.processing")}</button>
          <button className="chip t" aria-pressed="false">{t("filters.needs_attention")}</button>
        </div>
      </div>

      {loading ? (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-12" />)}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-12 text-text-muted">
          <svg className="i" style={{ width: 40, height: 40, margin: "0 auto 12px" }}><use href="#i-paper"/></svg>
          <p className="t">{t("papers.no_papers")}</p>
        </div>
      ) : (
        <div className="tbl">
          <table>
            <thead>
              <tr>
                <th className="t">{t("papers.col_title")}</th>
                <th className="t">{t("papers.col_year")}</th>
                <th className="t">{t("papers.col_journal")}</th>
                <th className="t">DOI</th>
                <th className="t">{t("papers.col_tags")}</th>
                <th className="t">{t("papers.col_status")}</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((doc) => (
                <tr key={doc.id} className="clk" onClick={() => navigate(`/papers/${doc.id}/viewer`)}>
                  <td>
                    <div className="ttl">{doc.title || doc.file_hash.slice(0, 12)}</div>
                    <div className="au">{doc.authors}</div>
                  </td>
                  <td className="mono">{doc.year || "—"}</td>
                  <td>{doc.journal || "—"}</td>
                  <td className="mono">{doc.doi || "—"}</td>
                  <td>
                  </td>
                  <td>
                    <Badge variant={
                      doc.processing_status === "completed" ? "success" :
                      doc.processing_status === "processing" ? "info" : "error"
                    }>
                      {doc.processing_status === "completed" ? t("papers.status_ready") :
                       doc.processing_status === "processing" ? t("papers.status_processing") :
                       t("papers.status_failed")}
                    </Badge>
                  </td>
                  <td>
                    {doc.processing_status !== "completed" ? (
                      <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); handleProcess(doc.id); }}>
                        <svg className="i"><use href="#i-spark"/></svg>
                        <span className="t">{t("papers.analyze")}</span>
                      </Button>
                    ) : (
                      <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); navigate(`/papers/${doc.id}/viewer`); }}>
                        <svg className="i"><use href="#i-search"/></svg>
                        <span className="t">{t("papers.find_in_paper")}</span>
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="pager">
            <span>1–{filtered.length} / {docs.length}</span>
            <div className="actions">
              <Button variant="ghost" size="sm" disabled>‹</Button>
              <Button variant="ghost" size="sm">›</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
