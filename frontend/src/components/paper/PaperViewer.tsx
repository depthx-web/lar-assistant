import { useState } from "react";
import { BookOpen, Search, Send } from "lucide-react";
import { useI18n } from "../../context/I18nContext";
import { cn } from "../ui/cn";

export default function PaperViewer({
  docId,
  onClose,
}: {
  docId: number;
  onClose?: () => void;
}) {
  const { t } = useI18n();
  const [activeSection, setActiveSection] = useState(0);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Array<{ role: "user" | "assistant"; content: string; sources?: any[] }>>([
    { role: "user", content: "What was the MRI acquisition protocol, and which software processed the scans?" },
    {
      role: "assistant",
      content: "The scans were T1-weighted on 3T scanners with 1 mm isotropic voxels, TR 2300 ms and TE 2.98 ms [1]. The paper does not name the processing software [2].",
      sources: [
        { type: "direct", paper: "Haddad et al. 2023", page: 7, section: "Methods" },
        { type: "inference", note: "The pipeline resembles common surface-based tools, but the paper never states which one." },
      ],
    },
  ]);

  const sections = [
    { name: t("sections.abstract"), page: 1 },
    { name: t("sections.introduction"), page: 2 },
    { name: t("sections.methods"), page: 5, current: true },
    { name: t("sections.results"), page: 8 },
    { name: t("sections.discussion"), page: 11 },
    { name: t("sections.references"), page: 14 },
  ];

  const scopeOptions = [
    t("scope.current_paper"),
    t("scope.selected_papers"),
    t("scope.current_journal"),
    t("scope.current_manuscript"),
    t("scope.knowledge_base"),
    t("scope.general_ai"),
  ];

  const quickChips = [
    t("chips.summarize"),
    t("chips.extract_results"),
    t("chips.extract_methods"),
    t("chips.extract_limitations"),
  ];

  const handleSend = async () => {
    if (!question.trim() || loading) return;
    const q = question.trim();
    setQuestion("");
    setMessages((m) => [...m, { role: "user", content: q }]);
    setLoading(true);
    try {
      const response = await fetch("/api/v1/rag/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q, top_k: 5 }),
      });
      const data = await response.json();
      if (data.answer) {
        setMessages((m) => [...m, { role: "assistant", content: data.answer, sources: data.sources }]);
      }
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "Error: Could not reach AI service. Ensure Ollama is running." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Doc header */}
      <div className="flex items-start gap-4 px-6 py-4 border-b border-border bg-surface">
        <button onClick={onClose} className="flex items-center gap-1 -ml-2 text-text-muted hover:text-text transition-colors">
          <BookOpen className="w-4 h-4 rotate-90" />
          <span className="text-sm">{t("papers.title")}</span>
        </button>
        <div className="flex-1 min-w-0">
          <h1 className="text-base font-semibold text-text leading-snug">
            Longitudinal hippocampal volume change in mild cognitive impairment
          </h1>
          <p className="text-xs text-text-muted mt-1 font-academic">
            Haddad, Lindqvist, Okafor<span className="text-text-faint mx-1">|</span>
            Journal of Applied Neuroimaging<span className="text-text-faint mx-1">|</span>
            2023<span className="text-text-faint mx-1">|</span>
            <span className="font-mono-a text-xs">10.5555/jan.2023.0412</span>
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-xs px-2 py-0.5 rounded-md bg-success-subtle text-success font-medium border border-success/20">
            {t("status.ready")}
          </span>
          <button className="flex items-center gap-1 px-3 py-1.5 text-xs border border-border rounded-lg text-text hover:bg-surface-2 transition-colors">
            <Search className="w-3.5 h-3.5" />
            <span>{t("papers.find_in_paper")}</span>
          </button>
          <button className="px-3 py-1.5 text-xs rounded-lg bg-primary text-primary-fg hover:bg-primary/90 transition-colors">
            <span>{t("papers.summarize")}</span>
          </button>
        </div>
      </div>

      {/* Three-pane body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Outline */}
        <aside className="w-[200px] border-r border-border overflow-y-auto bg-surface shrink-0">
          <div className="px-3 py-2 text-[11px] font-semibold uppercase tracking-wider text-text-faint">
            {t("sections.title")}
          </div>
          {sections.map((s, i) => (
            <button
              key={i}
              onClick={() => setActiveSection(i)}
              className={cn(
                "w-full text-start px-3 py-1.5 text-sm flex items-center justify-between transition-colors",
                s.current ? "bg-primary-subtle text-primary font-medium" : "text-text-muted hover:bg-surface-2 hover:text-text"
              )}
            >
              <span className="truncate">{s.name}</span>
              <span className="text-[10px] font-mono-a text-text-faint">{s.page}</span>
            </button>
          ))}
        </aside>

        {/* Center: Document */}
        <div className="flex-1 overflow-y-auto p-6 bg-bg">
          <article className="max-w-[680px] mx-auto">
            <p className="text-[11px] uppercase tracking-widest text-text-faint mb-4 font-academic">
              PAGE 7 · <span className="text-text-muted font-medium">{sections[2].name}</span>
            </p>
            <h3 className="text-lg font-semibold text-text mb-4 font-academic">2.3 Image acquisition</h3>
            <div className="text-[15px] leading-relaxed text-text font-read">
              <p className="mb-4">
                All participants were scanned on 3T systems using a T1-weighted magnetization-prepared sequence.{" "}
                <mark className="bg-[#FFF0B8] dark:bg-[#4A3F12] text-inherit px-1 rounded">
                  Acquisition used a 1 mm isotropic voxel size, a repetition time of 2300 ms and an echo time of 2.98 ms
                </mark>{" "}
                at each of the four sites <sup className="text-accent text-xs">[4]</sup>.
              </p>
              <div className="flex gap-2 my-4">
                {["Ask AI", "Summarize", "Add to notes"].map((label) => (
                  <button
                    key={label}
                    className="px-3 py-1.5 text-xs bg-[#1A2130] text-white dark:bg-[#E7EAF1] dark:text-[#10131A] rounded hover:opacity-90 transition-opacity font-academic"
                  >
                    {t(`action.${label.toLowerCase().replace(/\s+/g, "_")}`)}
                  </button>
                ))}
              </div>
              <p className="mb-4">
                Scans were visually inspected for motion artefacts before processing. Cortical and subcortical volumes
                were estimated with an automated pipeline, and hippocampal volumes were normalised to total
                intracranial volume <sup className="text-accent text-xs">[7]</sup>.
              </p>
              <p>
                Follow-up scans were acquired at 12 and 24 months. Participants with fewer than two usable scans
                were excluded from the longitudinal analysis.
              </p>
            </div>
          </article>
        </div>

        {/* Right: AI Chat */}
        <aside className="w-[360px] border-l border-border flex flex-col bg-surface shrink-0">
          <div className="px-4 py-3 border-b border-border">
            <p className="text-xs font-semibold uppercase tracking-wider text-text-faint mb-2 font-academic">
              {t("ai.ask_about")}
            </p>
            <div className="grid grid-cols-2 gap-1.5">
              {scopeOptions.map((opt, i) => (
                <label key={i} className="flex items-center gap-1.5 text-xs text-text-muted cursor-pointer py-0.5">
                  <input type="radio" name="scope" defaultChecked={i === 0} className="accent-primary w-3 h-3" />
                  <span className="truncate">{opt}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
            {messages.map((msg, i) => (
              <div key={i} className={msg.role === "user" ? "flex justify-end" : "flex justify-start"}>
                <div
                  className={cn(
                    "max-w-[92%] rounded-xl px-3 py-2 text-sm leading-relaxed",
                    msg.role === "user"
                      ? "bg-primary-subtle text-primary rounded-br-none"
                      : "bg-transparent text-text"
                  )}
                >
                  {msg.content}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-2 space-y-2">
                      {msg.sources.map((src, j) => (
                        <div key={j} className="border border-border rounded-md p-2 bg-bg text-xs">
                          <div className="flex items-center gap-1.5 mb-1">
                            <span className={src.type === "direct" ? "text-success" : "text-warning"}>
                              {src.type === "direct" ? t("evidence.direct") : t("evidence.inference")}
                            </span>
                          </div>
                          {src.type === "direct" && (
                            <dl className="grid grid-cols-[auto_1fr] gap-x-2">
                              <dt className="text-text-faint">{t("evidence.paper")}:</dt>
                              <dd className="text-text">{src.paper}</dd>
                              <dt className="text-text-faint">{t("evidence.page")}:</dt>
                              <dd className="text-text font-mono-a">{src.page}</dd>
                              <dt className="text-text-faint">{t("evidence.section")}:</dt>
                              <dd className="text-text">{src.section}</dd>
                            </dl>
                          )}
                          {src.type === "inference" && <p className="text-text-muted mt-1">{src.note}</p>}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="max-w-[92%] rounded-xl px-3 py-2 bg-surface-2 text-text text-sm flex items-center gap-2 border border-border">
                  <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  {t("chat.thinking")}…
                </div>
              </div>
            )}
          </div>

          <div className="border-t border-border p-3 flex flex-col gap-2">
            <div className="flex flex-wrap gap-1.5">
              {quickChips.map((c) => (
                <button
                  key={c}
                  onClick={() => setQuestion(c)}
                  className="px-2.5 py-1 text-xs rounded-lg border border-border bg-surface-2 text-text-muted hover:text-text hover:border-border-strong transition-colors"
                >
                  {c}
                </button>
              ))}
            </div>
            <div className="flex gap-2 items-end">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), handleSend())}
                placeholder={t("ai.ask_paper")}
                rows={2}
                className="flex-1 resize-none text-sm bg-surface border border-border-strong rounded-lg px-3 py-2 text-text placeholder-text-faint focus:border-primary focus:ring-1 focus:ring-primary/20 outline-none transition-colors"
              />
              <button
                onClick={handleSend}
                disabled={loading || !question.trim()}
                className="px-2.5 h-[42px] flex items-center justify-center shrink-0 rounded-lg bg-primary text-primary-fg disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
            <p className="text-[11px] text-text-faint font-academic">
              <kbd className="kbd">Ctrl /</kbd> {t("ai.focus_assistant")}
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}