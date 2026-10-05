import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from "react";
import api from "../lib/api";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Skeleton } from "../components/ui/Skeleton";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../components/ui/Toast";
import { useNavigate } from "react-router-dom";
export default function PapersPage() {
    const { t } = useI18n();
    const { addToast } = useToast();
    const navigate = useNavigate();
    const [docs, setDocs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [uploading, setUploading] = useState(false);
    const [uploadError, setUploadError] = useState(null);
    const loadDocs = () => {
        setLoading(true);
        api.get("/documents")
            .then((r) => { setDocs(r.data.documents ?? []); setLoading(false); })
            .catch(() => setLoading(false));
    };
    useEffect(() => { loadDocs(); }, []);
    const filtered = docs.filter((d) => d.title?.toLowerCase().includes(search.toLowerCase()) ||
        d.authors?.toLowerCase().includes(search.toLowerCase()) ||
        d.file_hash.toLowerCase().includes(search.toLowerCase()));
    const handleUpload = async (e) => {
        const file = e.target.files?.[0];
        if (!file)
            return;
        setUploading(true);
        setUploadError(null);
        const form = new FormData();
        form.append("file", file);
        try {
            await api.post("/documents/upload", form, { headers: { "Content-Type": "multipart/form-data" } });
            addToast({ variant: "success", title: t("papers.upload_success"), description: file.name });
            loadDocs();
        }
        catch (err) {
            const msg = err.response?.data?.detail ?? t("common.error");
            setUploadError(msg);
            addToast({ variant: "error", title: t("papers.upload_failed"), description: msg });
        }
        finally {
            setUploading(false);
            e.target.value = "";
        }
    };
    const handleProcess = async (id) => {
        try {
            await api.post(`/documents/${id}/process`);
            addToast({ variant: "success", title: t("papers.analyzed") });
            loadDocs();
        }
        catch (err) {
            addToast({ variant: "error", title: t("common.error"), description: err.response?.data?.detail ?? "Processing failed" });
        }
    };
    return (_jsxs("div", { className: "screen", children: [_jsxs("div", { className: "pagehead", children: [_jsxs("div", { children: [_jsx("h1", { className: "t", children: t("papers.title") }), _jsx("p", { className: "sub", children: t("papers.documents_count", { count: docs.length }) })] }), _jsxs("div", { className: "actions", children: [_jsxs("label", { className: "cursor-pointer", children: [_jsx("input", { type: "file", accept: ".pdf,.docx,.txt", className: "hidden", onChange: handleUpload }), _jsxs(Button, { variant: "secondary", size: "sm", loading: uploading, children: [_jsx("svg", { className: "i", children: _jsx("use", { href: "#i-upload" }) }), _jsx("span", { className: "t", children: t("papers.upload") })] })] }), _jsx(Button, { variant: "ghost", size: "sm", onClick: loadDocs, children: _jsx("svg", { className: "i", children: _jsx("use", { href: "#i-refresh" }) }) })] })] }), uploadError && (_jsxs("div", { className: "alert", role: "alert", children: [_jsx("svg", { className: "i", children: _jsx("use", { href: "#i-alert" }) }), _jsxs("div", { children: [_jsx("h3", { children: t("papers.upload_failed") }), _jsx("p", { children: uploadError })] })] })), _jsxs("div", { className: "drop", children: [_jsx("svg", { className: "i", children: _jsx("use", { href: "#i-upload" }) }), _jsxs("div", { children: [_jsx("b", { className: "t", children: t("papers.drop_files") }), _jsx("span", { className: "t", children: t("papers.drop_desc") })] })] }), _jsxs("div", { className: "toolbar", children: [_jsx("input", { className: "field srch", type: "search", placeholder: t("papers.search_papers"), value: search, onChange: (e) => setSearch(e.target.value) }), _jsxs("div", { className: "chips", role: "group", children: [_jsx("button", { className: "chip t", "aria-pressed": "true", children: t("filters.all") }), _jsx("button", { className: "chip t", "aria-pressed": "false", children: t("filters.ready") }), _jsx("button", { className: "chip t", "aria-pressed": "false", children: t("filters.processing") }), _jsx("button", { className: "chip t", "aria-pressed": "false", children: t("filters.needs_attention") })] })] }), loading ? (_jsx("div", { className: "space-y-2", children: [1, 2, 3].map((i) => _jsx(Skeleton, { className: "h-12" }, i)) })) : filtered.length === 0 ? (_jsxs("div", { className: "text-center py-12 text-text-muted", children: [_jsx("svg", { className: "i", style: { width: 40, height: 40, margin: "0 auto 12px" }, children: _jsx("use", { href: "#i-paper" }) }), _jsx("p", { className: "t", children: t("papers.no_papers") })] })) : (_jsxs("div", { className: "tbl", children: [_jsxs("table", { children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { className: "t", children: t("papers.col_title") }), _jsx("th", { className: "t", children: t("papers.col_year") }), _jsx("th", { className: "t", children: t("papers.col_journal") }), _jsx("th", { className: "t", children: "DOI" }), _jsx("th", { className: "t", children: t("papers.col_tags") }), _jsx("th", { className: "t", children: t("papers.col_status") }), _jsx("th", {})] }) }), _jsx("tbody", { children: filtered.map((doc) => (_jsxs("tr", { className: "clk", onClick: () => navigate(`/papers/${doc.id}/viewer`), children: [_jsxs("td", { children: [_jsx("div", { className: "ttl", children: doc.title || doc.file_hash.slice(0, 12) }), _jsx("div", { className: "au", children: doc.authors })] }), _jsx("td", { className: "mono", children: doc.year || "—" }), _jsx("td", { children: doc.journal || "—" }), _jsx("td", { className: "mono", children: doc.doi || "—" }), _jsx("td", {}), _jsx("td", { children: _jsx(Badge, { variant: doc.processing_status === "completed" ? "success" :
                                                    doc.processing_status === "processing" ? "info" : "error", children: doc.processing_status === "completed" ? t("papers.status_ready") :
                                                    doc.processing_status === "processing" ? t("papers.status_processing") :
                                                        t("papers.status_failed") }) }), _jsx("td", { children: doc.processing_status !== "completed" ? (_jsxs(Button, { variant: "ghost", size: "sm", onClick: (e) => { e.stopPropagation(); handleProcess(doc.id); }, children: [_jsx("svg", { className: "i", children: _jsx("use", { href: "#i-spark" }) }), _jsx("span", { className: "t", children: t("papers.analyze") })] })) : (_jsxs(Button, { variant: "ghost", size: "sm", onClick: (e) => { e.stopPropagation(); navigate(`/papers/${doc.id}/viewer`); }, children: [_jsx("svg", { className: "i", children: _jsx("use", { href: "#i-search" }) }), _jsx("span", { className: "t", children: t("papers.find_in_paper") })] })) })] }, doc.id))) })] }), _jsxs("div", { className: "pager", children: [_jsxs("span", { children: ["1\u2013", filtered.length, " / ", docs.length] }), _jsxs("div", { className: "actions", children: [_jsx(Button, { variant: "ghost", size: "sm", disabled: true, children: "\u2039" }), _jsx(Button, { variant: "ghost", size: "sm", children: "\u203A" })] })] })] }))] }));
}
