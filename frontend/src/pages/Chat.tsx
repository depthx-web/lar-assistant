import { useState, useRef, useEffect, useCallback } from "react";
import { useI18n } from "../context/I18nContext";
import { Card, PageHeader } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { Badge } from "../components/ui/Badge";
import { Send, Loader2, Trash2, Bot, FileText, BookOpen, ChevronDown, ChevronUp, X } from "lucide-react";
import api from "../lib/api";
import { useToast } from "../components/ui/Toast";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Array<{ source_id: number; document_title: string; similarity: number; content_preview: string }>;
}

interface Document {
  id: number;
  title: string | null;
  filename: string;
  document_type: string;
  processing_status: string;
}

const STORAGE_KEY = "lara_chat_history";

function loadHistory(): Message[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveHistory(messages: Message[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-50)));
  } catch { /* storage full */ }
}

export default function ChatPage() {
  const { t } = useI18n();
  const { addToast } = useToast();
  const [messages, setMessages] = useState<Message[]>(loadHistory);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<number | null>(null);
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
    } catch {
      // ignore
    } finally {
      setDocLoading(false);
    }
  };

  const processDocument = async (docId: number) => {
    try {
      await api.post(`/documents/${docId}/process`);
      addToast({ variant: "success", title: t("papers.analyzed") });
      loadDocuments();
    } catch {
      addToast({ variant: "error", title: t("common.error") });
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
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

      const assistantMsg: Message = { role: "assistant", content: "", sources: [] };

      setMessages((m) => [...m, assistantMsg]);

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
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
      } catch {
        // sources fetch failed, no big deal
      }
    } catch (err: any) {
      setMessages((m) => [...m, { role: "assistant", content: err.message || t("common.error") }]);
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = () => {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
    addToast({ variant: "info", title: t("chat.history_cleared") });
  };

  const selectedDocTitle = documents.find((d) => d.id === selectedDoc)?.title || documents.find((d) => d.id === selectedDoc)?.filename;

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      <PageHeader
        title={t("chat.title")}
        subtitle={t("chat.subtitle")}
        action={
          messages.length > 0 && (
            <Button variant="ghost" size="sm" onClick={clearHistory}>
              <Trash2 className="w-4 h-4" />
            </Button>
          )
        }
      />

      {/* Document selector */}
      <Card>
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => setShowDocs(!showDocs)}
            className="flex items-center gap-2 px-3 py-2 text-sm bg-surface-2 border border-border rounded-lg hover:bg-surface-3 transition-colors"
          >
            <BookOpen className="w-4 h-4" />
            {selectedDocTitle ? t("chat.querying_doc") : t("chat.query_all_docs")}
            {showDocs ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          {selectedDoc && (
            <Badge variant="info" className="flex items-center gap-1">
              {selectedDocTitle}
              <button onClick={() => setSelectedDoc(null)} className="ml-1">
                <X className="w-3 h-3" />
              </button>
            </Badge>
          )}
        </div>
        {showDocs && (
          <div className="mt-3 space-y-2">
            {docLoading ? (
              <p className="text-sm text-text-muted">{t("common.loading")}</p>
            ) : documents.length === 0 ? (
              <p className="text-sm text-text-muted">{t("chat.no_documents")}</p>
            ) : (
              <div className="space-y-1 max-h-48 overflow-y-auto">
                {documents.map((doc) => (
                  <button
                    key={doc.id}
                    onClick={() => {
                      setSelectedDoc(doc.id === selectedDoc ? null : doc.id);
                      setShowDocs(false);
                    }}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors ${
                      selectedDoc === doc.id
                        ? "bg-primary/10 text-primary"
                        : "text-text hover:bg-surface-2"
                    }`}
                  >
                    <span className="truncate flex-1 text-start">{doc.title || doc.filename}</span>
                    <Badge variant={doc.processing_status?.toLowerCase() === "completed" ? "success" : "warning"}>
                      {doc.processing_status?.toLowerCase() === "completed" ? t("papers.status_completed") : t("papers.status_processing")}
                    </Badge>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </Card>

      {/* Chat messages */}
      <Card className="flex flex-col min-h-[60vh]">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Bot className="w-10 h-10 text-text-faint mb-3" />
              <p className="text-sm text-text-muted">{t("chat.ask")}</p>
              <p className="text-xs text-text-faint mt-2">{t("chat.rag_hint")}</p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className="max-w-[85%] space-y-1">
                <div className={`rounded-lg px-4 py-2 text-sm whitespace-pre-wrap ${
                  msg.role === "user"
                    ? "bg-primary text-primary-fg"
                    : "bg-surface-2 text-text border border-border"
                }`}>
                  {msg.content}
                </div>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="space-y-1">
                    {msg.sources.map((src) => (
                      <div key={src.source_id} className="flex items-start gap-2 px-3 py-2 bg-surface border border-border rounded-lg text-xs">
                        <FileText className="w-3 h-3 text-text-faint shrink-0 mt-0.5" />
                        <div className="min-w-0 flex-1">
                          <p className="font-medium text-text truncate">[{src.source_id}] {src.document_title}</p>
                          <p className="text-text-muted mt-0.5">{src.content_preview}</p>
                          <p className="text-text-faint mt-1">similarity: {src.similarity.toFixed(3)}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="max-w-[85%] rounded-lg px-4 py-2 bg-surface-2 text-text text-sm flex items-center gap-2 border border-border">
                <Loader2 className="w-4 h-4 animate-spin" />
                {t("chat.thinking") + "…"}
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
        <div className="border-t border-border p-3 flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={t("chat.ask")}
            onKeyDown={(e: any) => e.key === "Enter" && !e.shiftKey && sendMessage()}
          />
          <Button onClick={sendMessage} disabled={loading || !input.trim()}>
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </Card>
      <p className="text-xs text-text-faint text-center">
        {messages.length > 0 ? `${messages.length} ${t("chat.messages")}` : ""}
      </p>
    </div>
  );
}
