import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
import { BookOpen, Search, Send } from "lucide-react";
import { useI18n } from "../../context/I18nContext";
import { cn } from "../ui/cn";
export default function PaperViewer({ docId, onClose, }) {
    const { t } = useI18n();
    const [activeSection, setActiveSection] = useState(0);
    const [question, setQuestion] = useState("");
    const [loading, setLoading] = useState(false);
    const [messages, setMessages] = useState([
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
        if (!question.trim() || loading)
            return;
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
        }
        catch (err) {
            setMessages((m) => [
                ...m,
                { role: "assistant", content: "Error: Could not reach AI service. Ensure Ollama is running." },
            ]);
        }
        finally {
            setLoading(false);
        }
    };
    return (_jsxs("div", { className: "flex flex-col h-full", children: [_jsxs("div", { className: "flex items-start gap-4 px-6 py-4 border-b border-border bg-surface", children: [_jsxs("button", { onClick: onClose, className: "flex items-center gap-1 -ml-2 text-text-muted hover:text-text transition-colors", children: [_jsx(BookOpen, { className: "w-4 h-4 rotate-90" }), _jsx("span", { className: "text-sm", children: t("papers.title") })] }), _jsxs("div", { className: "flex-1 min-w-0", children: [_jsx("h1", { className: "text-base font-semibold text-text leading-snug", children: "Longitudinal hippocampal volume change in mild cognitive impairment" }), _jsxs("p", { className: "text-xs text-text-muted mt-1 font-academic", children: ["Haddad, Lindqvist, Okafor", _jsx("span", { className: "text-text-faint mx-1", children: "|" }), "Journal of Applied Neuroimaging", _jsx("span", { className: "text-text-faint mx-1", children: "|" }), "2023", _jsx("span", { className: "text-text-faint mx-1", children: "|" }), _jsx("span", { className: "font-mono-a text-xs", children: "10.5555/jan.2023.0412" })] })] }), _jsxs("div", { className: "flex items-center gap-2 shrink-0", children: [_jsx("span", { className: "text-xs px-2 py-0.5 rounded-md bg-success-subtle text-success font-medium border border-success/20", children: t("status.ready") }), _jsxs("button", { className: "flex items-center gap-1 px-3 py-1.5 text-xs border border-border rounded-lg text-text hover:bg-surface-2 transition-colors", children: [_jsx(Search, { className: "w-3.5 h-3.5" }), _jsx("span", { children: t("papers.find_in_paper") })] }), _jsx("button", { className: "px-3 py-1.5 text-xs rounded-lg bg-primary text-primary-fg hover:bg-primary/90 transition-colors", children: _jsx("span", { children: t("papers.summarize") }) })] })] }), _jsxs("div", { className: "flex-1 flex overflow-hidden", children: [_jsxs("aside", { className: "w-[200px] border-r border-border overflow-y-auto bg-surface shrink-0", children: [_jsx("div", { className: "px-3 py-2 text-[11px] font-semibold uppercase tracking-wider text-text-faint", children: t("sections.title") }), sections.map((s, i) => (_jsxs("button", { onClick: () => setActiveSection(i), className: cn("w-full text-start px-3 py-1.5 text-sm flex items-center justify-between transition-colors", s.current ? "bg-primary-subtle text-primary font-medium" : "text-text-muted hover:bg-surface-2 hover:text-text"), children: [_jsx("span", { className: "truncate", children: s.name }), _jsx("span", { className: "text-[10px] font-mono-a text-text-faint", children: s.page })] }, i)))] }), _jsx("div", { className: "flex-1 overflow-y-auto p-6 bg-bg", children: _jsxs("article", { className: "max-w-[680px] mx-auto", children: [_jsxs("p", { className: "text-[11px] uppercase tracking-widest text-text-faint mb-4 font-academic", children: ["PAGE 7 \u00B7 ", _jsx("span", { className: "text-text-muted font-medium", children: sections[2].name })] }), _jsx("h3", { className: "text-lg font-semibold text-text mb-4 font-academic", children: "2.3 Image acquisition" }), _jsxs("div", { className: "text-[15px] leading-relaxed text-text font-read", children: [_jsxs("p", { className: "mb-4", children: ["All participants were scanned on 3T systems using a T1-weighted magnetization-prepared sequence.", " ", _jsx("mark", { className: "bg-[#FFF0B8] dark:bg-[#4A3F12] text-inherit px-1 rounded", children: "Acquisition used a 1 mm isotropic voxel size, a repetition time of 2300 ms and an echo time of 2.98 ms" }), " ", "at each of the four sites ", _jsx("sup", { className: "text-accent text-xs", children: "[4]" }), "."] }), _jsx("div", { className: "flex gap-2 my-4", children: ["Ask AI", "Summarize", "Add to notes"].map((label) => (_jsx("button", { className: "px-3 py-1.5 text-xs bg-[#1A2130] text-white dark:bg-[#E7EAF1] dark:text-[#10131A] rounded hover:opacity-90 transition-opacity font-academic", children: t(`action.${label.toLowerCase().replace(/\s+/g, "_")}`) }, label))) }), _jsxs("p", { className: "mb-4", children: ["Scans were visually inspected for motion artefacts before processing. Cortical and subcortical volumes were estimated with an automated pipeline, and hippocampal volumes were normalised to total intracranial volume ", _jsx("sup", { className: "text-accent text-xs", children: "[7]" }), "."] }), _jsx("p", { children: "Follow-up scans were acquired at 12 and 24 months. Participants with fewer than two usable scans were excluded from the longitudinal analysis." })] })] }) }), _jsxs("aside", { className: "w-[360px] border-l border-border flex flex-col bg-surface shrink-0", children: [_jsxs("div", { className: "px-4 py-3 border-b border-border", children: [_jsx("p", { className: "text-xs font-semibold uppercase tracking-wider text-text-faint mb-2 font-academic", children: t("ai.ask_about") }), _jsx("div", { className: "grid grid-cols-2 gap-1.5", children: scopeOptions.map((opt, i) => (_jsxs("label", { className: "flex items-center gap-1.5 text-xs text-text-muted cursor-pointer py-0.5", children: [_jsx("input", { type: "radio", name: "scope", defaultChecked: i === 0, className: "accent-primary w-3 h-3" }), _jsx("span", { className: "truncate", children: opt })] }, i))) })] }), _jsxs("div", { className: "flex-1 overflow-y-auto p-4 space-y-4 min-h-0", children: [messages.map((msg, i) => (_jsx("div", { className: msg.role === "user" ? "flex justify-end" : "flex justify-start", children: _jsxs("div", { className: cn("max-w-[92%] rounded-xl px-3 py-2 text-sm leading-relaxed", msg.role === "user"
                                                ? "bg-primary-subtle text-primary rounded-br-none"
                                                : "bg-transparent text-text"), children: [msg.content, msg.sources && msg.sources.length > 0 && (_jsx("div", { className: "mt-2 space-y-2", children: msg.sources.map((src, j) => (_jsxs("div", { className: "border border-border rounded-md p-2 bg-bg text-xs", children: [_jsx("div", { className: "flex items-center gap-1.5 mb-1", children: _jsx("span", { className: src.type === "direct" ? "text-success" : "text-warning", children: src.type === "direct" ? t("evidence.direct") : t("evidence.inference") }) }), src.type === "direct" && (_jsxs("dl", { className: "grid grid-cols-[auto_1fr] gap-x-2", children: [_jsxs("dt", { className: "text-text-faint", children: [t("evidence.paper"), ":"] }), _jsx("dd", { className: "text-text", children: src.paper }), _jsxs("dt", { className: "text-text-faint", children: [t("evidence.page"), ":"] }), _jsx("dd", { className: "text-text font-mono-a", children: src.page }), _jsxs("dt", { className: "text-text-faint", children: [t("evidence.section"), ":"] }), _jsx("dd", { className: "text-text", children: src.section })] })), src.type === "inference" && _jsx("p", { className: "text-text-muted mt-1", children: src.note })] }, j))) }))] }) }, i))), loading && (_jsx("div", { className: "flex justify-start", children: _jsxs("div", { className: "max-w-[92%] rounded-xl px-3 py-2 bg-surface-2 text-text text-sm flex items-center gap-2 border border-border", children: [_jsxs("svg", { className: "animate-spin w-4 h-4", viewBox: "0 0 24 24", fill: "none", children: [_jsx("circle", { className: "opacity-25", cx: "12", cy: "12", r: "10", stroke: "currentColor", strokeWidth: "4" }), _jsx("path", { className: "opacity-75", fill: "currentColor", d: "M4 12a8 8 0 018-8v8H4z" })] }), t("chat.thinking"), "\u2026"] }) }))] }), _jsxs("div", { className: "border-t border-border p-3 flex flex-col gap-2", children: [_jsx("div", { className: "flex flex-wrap gap-1.5", children: quickChips.map((c) => (_jsx("button", { onClick: () => setQuestion(c), className: "px-2.5 py-1 text-xs rounded-lg border border-border bg-surface-2 text-text-muted hover:text-text hover:border-border-strong transition-colors", children: c }, c))) }), _jsxs("div", { className: "flex gap-2 items-end", children: [_jsx("textarea", { value: question, onChange: (e) => setQuestion(e.target.value), onKeyDown: (e) => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), handleSend()), placeholder: t("ai.ask_paper"), rows: 2, className: "flex-1 resize-none text-sm bg-surface border border-border-strong rounded-lg px-3 py-2 text-text placeholder-text-faint focus:border-primary focus:ring-1 focus:ring-primary/20 outline-none transition-colors" }), _jsx("button", { onClick: handleSend, disabled: loading || !question.trim(), className: "px-2.5 h-[42px] flex items-center justify-center shrink-0 rounded-lg bg-primary text-primary-fg disabled:opacity-50", children: _jsx(Send, { className: "w-4 h-4" }) })] }), _jsxs("p", { className: "text-[11px] text-text-faint font-academic", children: [_jsx("kbd", { className: "kbd", children: "Ctrl /" }), " ", t("ai.focus_assistant")] })] })] })] })] }));
}
