import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useRef, useEffect } from "react";
import { useI18n } from "../context/I18nContext";
import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { Badge } from "../components/ui/Badge";
import { Send, Loader2, Trash2, Bot, FileText, BookOpen, ChevronDown, ChevronUp, X } from "lucide-react";
import api from "../lib/api";
import { useToast } from "../components/ui/Toast";
const STORAGE_KEY = "lara_chat_history";
function loadHistory() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
    }
    catch {
        return [];
    }
}
function saveHistory(messages) {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-50)));
    }
    catch { /* storage full */ }
}
export default function ChatPage() {
    const { t } = useI18n();
    const { addToast } = useToast();
    const [messages, setMessages] = useState(loadHistory);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const bottomRef = useRef(null);
    const [documents, setDocuments] = useState([]);
    const [selectedDoc, setSelectedDoc] = useState(null);
    const [docLoading, setDocLoading] = useState(false);
    const [showDocs, setShowDocs] = useState(false);
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, loading]);
    useEffect(() => {
        saveHistory(messages);
    }, [messages]);
    useEffect(() => {
        loadDocuments();
    }, []);
    const loadDocuments = async () => {
        setDocLoading(true);
        try {
            const res = await api.get("/documents");
            setDocuments(res.data.documents || []);
        }
        catch {
            // ignore
        }
        finally {
            setDocLoading(false);
        }
    };
    const processDocument = async (docId) => {
        try {
            await api.post(`/documents/${docId}/process`);
            addToast({ variant: "success", title: t("papers.analyzed") });
            loadDocuments();
        }
        catch {
            addToast({ variant: "error", title: t("common.error") });
        }
    };
    const sendMessage = async () => {
        if (!input.trim() || loading)
            return;
        const userMsg = input.trim();
        setInput("");
        setMessages((m) => [...m, { role: "user", content: userMsg }]);
        setLoading(true);
        try {
            // Use streaming RAG endpoint
            const response = await fetch("/api/v1/rag/ask/stream", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    question: userMsg,
                    document_id: selectedDoc,
                    top_k: 5,
                    temperature: 0.7,
                }),
            });
            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                throw new Error(err.detail || t("common.error"));
            }
            // SSE streaming
            const reader = response.body?.getReader();
            const decoder = new TextDecoder();
            let assistantContent = "";
            const assistantMsg = { role: "assistant", content: "", sources: [] };
            setMessages((m) => [...m, assistantMsg]);
            if (reader) {
                while (true) {
                    const { done, value } = await reader.read();
                    if (done)
                        break;
                    const chunk = decoder.decode(value);
                    const lines = chunk.split("\n");
                    for (const line of lines) {
                        if (line.startsWith("data: ")) {
                            const data = line.slice(6).trim();
                            if (data) {
                                assistantContent += data;
                                setMessages((m) => {
                                    const last = [...m];
                                    last[last.length - 1] = { ...last[last.length - 1], content: assistantContent };
                                    return last;
                                });
                            }
                        }
                    }
                }
            }
            // Fetch sources separately via non-streaming endpoint
            try {
                const sourcesRes = await api.post("/rag/ask", {
                    question: userMsg,
                    document_id: selectedDoc,
                    top_k: 5,
                    temperature: 0.7,
                });
                const sources = sourcesRes.data.sources || [];
                setMessages((m) => {
                    const last = [...m];
                    last[last.length - 1] = { ...last[last.length - 1], sources };
                    return last;
                });
            }
            catch {
                // sources fetch failed, no big deal
            }
        }
        catch (err) {
            setMessages((m) => [...m, { role: "assistant", content: err.message || t("common.error") }]);
        }
        finally {
            setLoading(false);
        }
    };
    const clearHistory = () => {
        setMessages([]);
        localStorage.removeItem(STORAGE_KEY);
        addToast({ variant: "info", title: t("chat.history_cleared") });
    };
    const selectedDocTitle = documents.find((d) => d.id === selectedDoc)?.title || documents.find((d) => d.id === selectedDoc)?.filename;
    return (_jsxs("div", { className: "max-w-3xl mx-auto space-y-4", children: [_jsx(PageHeader, { title: t("chat.title"), subtitle: t("chat.subtitle"), action: messages.length > 0 && (_jsx(Button, { variant: "ghost", size: "sm", onClick: clearHistory, children: _jsx(Trash2, { className: "w-4 h-4" }) })) }), _jsxs(Card, { children: [_jsxs("div", { className: "flex items-center gap-2 flex-wrap", children: [_jsxs("button", { onClick: () => setShowDocs(!showDocs), className: "flex items-center gap-2 px-3 py-2 text-sm bg-surface-2 border border-border rounded-lg hover:bg-surface-3 transition-colors", children: [_jsx(BookOpen, { className: "w-4 h-4" }), selectedDocTitle ? t("chat.querying_doc") : t("chat.query_all_docs"), showDocs ? _jsx(ChevronUp, { className: "w-4 h-4" }) : _jsx(ChevronDown, { className: "w-4 h-4" })] }), selectedDoc && (_jsxs(Badge, { variant: "info", className: "flex items-center gap-1", children: [selectedDocTitle, _jsx("button", { onClick: () => setSelectedDoc(null), className: "ml-1", children: _jsx(X, { className: "w-3 h-3" }) })] }))] }), showDocs && (_jsx("div", { className: "mt-3 space-y-2", children: docLoading ? (_jsx("p", { className: "text-sm text-text-muted", children: t("common.loading") })) : documents.length === 0 ? (_jsx("p", { className: "text-sm text-text-muted", children: t("chat.no_documents") })) : (_jsx("div", { className: "space-y-1 max-h-48 overflow-y-auto", children: documents.map((doc) => (_jsxs("button", { onClick: () => {
                                    setSelectedDoc(doc.id === selectedDoc ? null : doc.id);
                                    setShowDocs(false);
                                }, className: `w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors ${selectedDoc === doc.id
                                    ? "bg-primary/10 text-primary"
                                    : "text-text hover:bg-surface-2"}`, children: [_jsx("span", { className: "truncate flex-1 text-start", children: doc.title || doc.filename }), _jsx(Badge, { variant: doc.processing_status?.toLowerCase() === "completed" ? "success" : "warning", children: doc.processing_status?.toLowerCase() === "completed" ? t("papers.status_completed") : t("papers.status_processing") })] }, doc.id))) })) }))] }), _jsxs(Card, { className: "flex flex-col min-h-[60vh]", children: [_jsxs("div", { className: "flex-1 overflow-y-auto p-4 space-y-4", children: [messages.length === 0 && (_jsxs("div", { className: "flex flex-col items-center justify-center py-12 text-center", children: [_jsx(Bot, { className: "w-10 h-10 text-text-faint mb-3" }), _jsx("p", { className: "text-sm text-text-muted", children: t("chat.ask") }), _jsx("p", { className: "text-xs text-text-faint mt-2", children: t("chat.rag_hint") })] })), messages.map((msg, i) => (_jsx("div", { className: `flex ${msg.role === "user" ? "justify-end" : "justify-start"}`, children: _jsxs("div", { className: "max-w-[85%] space-y-1", children: [_jsx("div", { className: `rounded-lg px-4 py-2 text-sm whitespace-pre-wrap ${msg.role === "user"
                                                ? "bg-primary text-primary-fg"
                                                : "bg-surface-2 text-text border border-border"}`, children: msg.content }), msg.sources && msg.sources.length > 0 && (_jsx("div", { className: "space-y-1", children: msg.sources.map((src) => (_jsxs("div", { className: "flex items-start gap-2 px-3 py-2 bg-surface border border-border rounded-lg text-xs", children: [_jsx(FileText, { className: "w-3 h-3 text-text-faint shrink-0 mt-0.5" }), _jsxs("div", { className: "min-w-0 flex-1", children: [_jsxs("p", { className: "font-medium text-text truncate", children: ["[", src.source_id, "] ", src.document_title] }), _jsx("p", { className: "text-text-muted mt-0.5", children: src.content_preview }), _jsxs("p", { className: "text-text-faint mt-1", children: ["similarity: ", src.similarity.toFixed(3)] })] })] }, src.source_id))) }))] }) }, i))), loading && (_jsx("div", { className: "flex justify-start", children: _jsxs("div", { className: "max-w-[85%] rounded-lg px-4 py-2 bg-surface-2 text-text text-sm flex items-center gap-2 border border-border", children: [_jsx(Loader2, { className: "w-4 h-4 animate-spin" }), t("chat.thinking") + "…"] }) })), _jsx("div", { ref: bottomRef })] }), _jsxs("div", { className: "border-t border-border p-3 flex gap-2", children: [_jsx(Input, { value: input, onChange: (e) => setInput(e.target.value), placeholder: t("chat.ask"), onKeyDown: (e) => e.key === "Enter" && !e.shiftKey && sendMessage() }), _jsx(Button, { onClick: sendMessage, disabled: loading || !input.trim(), children: _jsx(Send, { className: "w-4 h-4" }) })] })] }), _jsx("p", { className: "text-xs text-text-faint text-center", children: messages.length > 0 ? `${messages.length} ${t("chat.messages")}` : "" })] }));
}
