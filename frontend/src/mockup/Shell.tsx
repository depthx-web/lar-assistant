import { useEffect, useRef, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { useUI } from "./UI";
import { SPRITE } from "./sprite";

export const ROUTES: Record<string, string> = {
  dashboard: "/",
  papers: "/papers",
  viewer: "/viewer",
  journals: "/journals",
  manuscript: "/manuscripts",
  compliance: "/compliance",
  reports: "/reports",
  models: "/models",
};

function keyFor(path: string) {
  const e = Object.entries(ROUTES).find(([, p]) => p === path);
  return e ? e[0] : "";
}

const CMDS: [string, string, string][] = [
  ["Search papers", "papers", "i-search"],
  ["Open manuscript", "manuscript", "i-edit"],
  ["Analyze manuscript", "manuscript", "i-spark"],
  ["Upload paper", "papers", "i-upload"],
  ["Open journal", "journals", "i-journal"],
  ["Run compliance check", "compliance", "i-shield"],
  ["Switch AI model", "models", "i-cpu"],
  ["Open settings", "models", "i-cpu"],
];

function load(k: string) { try { return localStorage.getItem(k); } catch { return null; } }
function store(k: string, v: string) { try { localStorage.setItem(k, v); } catch { /* ignore */ } }

export default function Shell() {
  const { tr, toggleLang, theme, cycleTheme, outage, toast, toastMsg } = useUI();
  const navigate = useNavigate();
  const loc = useLocation();
  const [collapsed, setCollapsed] = useState(() => load("ara-sb") === "1");
  const [pal, setPal] = useState(false);
  const [q, setQ] = useState("");
  const [idx, setIdx] = useState(0);
  const mainRef = useRef<HTMLElement>(null);
  const palIn = useRef<HTMLInputElement>(null);
  const palList = useRef<HTMLUListElement>(null);
  const fState = useRef("all");

  const cur = keyFor(loc.pathname);
  const navKey = cur === "viewer" ? "papers" : cur;

  const shown = CMDS.filter(([label]) => {
    const ql = q.toLowerCase();
    return !ql || tr(label).toLowerCase().includes(ql) || label.toLowerCase().includes(ql);
  });

  const go = (name: string) => {
    const p = ROUTES[name];
    if (p) navigate(p);
    setPal(false);
  };

  const openPal = () => { setQ(""); setIdx(0); setPal(true); };

  useEffect(() => {
    if (mainRef.current) mainRef.current.scrollTop = 0;
    fState.current = "all";
  }, [loc.pathname]);

  useEffect(() => { if (pal) palIn.current?.focus(); }, [pal]);

  // Delegated behaviours copied from the mockup script
  useEffect(() => {
    const filterPapers = () => {
      const s = document.getElementById("paperSearch") as HTMLInputElement | null;
      const qq = (s?.value || "").toLowerCase();
      document.querySelectorAll<HTMLElement>("#paperTbl tbody tr").forEach((r) => {
        const ok = (fState.current === "all" || r.dataset.status === fState.current) &&
          (!qq || (r.textContent || "").toLowerCase().includes(qq));
        r.hidden = !ok;
      });
    };
    const onClick = (e: MouseEvent) => {
      const t = e.target as HTMLElement;
      if (!t || !t.closest) return;
      const tab = t.closest<HTMLElement>('[role="tab"][data-tab]');
      if (tab) {
        const g = tab.closest(".tabgroup");
        if (g) {
          g.querySelectorAll(":scope > .tabs [data-tab]").forEach((x) => x.setAttribute("aria-selected", x === tab ? "true" : "false"));
          g.querySelectorAll<HTMLElement>(":scope > [data-pane]").forEach((p) => { p.hidden = p.dataset.pane !== tab.dataset.tab; });
        }
        return;
      }
      const tblBtn = t.closest<HTMLElement>("#paperTbl button");
      if (tblBtn) { e.stopPropagation(); toast((tblBtn.textContent || "").trim()); return; }
      const chip = t.closest<HTMLElement>(".chip[data-f]");
      if (chip) {
        fState.current = chip.dataset.f || "all";
        document.querySelectorAll(".chip[data-f]").forEach((x) => x.setAttribute("aria-pressed", x === chip ? "true" : "false"));
        filterPapers();
        return;
      }
      const th = t.closest<HTMLElement>("#paperTbl th[data-sort]");
      if (th) {
        const i = Number(th.dataset.sort);
        const asc = th.getAttribute("aria-sort") !== "ascending";
        document.querySelectorAll("#paperTbl th").forEach((x) => x.removeAttribute("aria-sort"));
        th.setAttribute("aria-sort", asc ? "ascending" : "descending");
        const body = document.querySelector("#paperTbl tbody");
        if (body) {
          const rows = Array.from(body.querySelectorAll<HTMLElement>(":scope > tr"));
          rows.sort((a, b) => {
            const x = (a.children[i]?.textContent || "").trim().toLowerCase();
            const y = (b.children[i]?.textContent || "").trim().toLowerCase();
            return (x < y ? -1 : x > y ? 1 : 0) * (asc ? 1 : -1);
          }).forEach((r) => body.appendChild(r));
        }
        return;
      }
      const g = t.closest<HTMLElement>("[data-go]");
      if (g && g.dataset.go) go(g.dataset.go);
    };
    const onInput = (e: Event) => {
      if ((e.target as HTMLElement)?.id === "paperSearch") filterPapers();
    };
    document.addEventListener("click", onClick);
    document.addEventListener("input", onInput);
    return () => {
      document.removeEventListener("click", onClick);
      document.removeEventListener("input", onInput);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [toast]);

  // Keyboard shortcuts
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const mod = e.ctrlKey || e.metaKey, k = e.key.toLowerCase();
      if (mod && (k === "k" || k === "p")) { e.preventDefault(); openPal(); }
      else if (mod && k === "s") { e.preventDefault(); toast(tr("Saved")); }
      else if (mod && k === "/") {
        e.preventDefault();
        const a = document.getElementById("aiInput1");
        if (cur === "viewer" && a) a.focus();
      } else if (e.key === "Escape") setPal(false);
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [cur, tr, toast]);

  const palKey = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!shown.length) return;
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      const n = (idx + (e.key === "ArrowDown" ? 1 : -1) + shown.length) % shown.length;
      setIdx(n);
      palList.current?.children[n]?.scrollIntoView({ block: "nearest" });
    }
    if (e.key === "Enter") { e.preventDefault(); go(shown[idx][1]); }
  };

  const toggleSb = () => {
    const c = !collapsed;
    store("ara-sb", c ? "1" : "0");
    setCollapsed(c);
  };

  const ac = (k: string) => (navKey === k ? ("page" as const) : undefined);

  return (
    <>
      <div style={{ position: "absolute", width: 0, height: 0, overflow: "hidden" }} aria-hidden="true" dangerouslySetInnerHTML={{ __html: SPRITE }} />
      <div className={"shell" + (collapsed ? " collapsed" : "")} id="shell">
        <header className="top">
          <button className="iconbtn" id="sbToggle" aria-label="Toggle sidebar" title="Toggle sidebar" onClick={toggleSb}><svg className="i"><use href="#i-panel" /></svg></button>
          <div className="brand"><span className="mark" aria-hidden="true">§</span><span className="nm t">{tr("Academic Research Assistant")}</span></div>
          <button className="proj" aria-label="Current project"><span className="faint t">{tr("Project")}</span><b>Hippocampal atrophy in MCI</b><svg className="i"><use href="#i-down" /></svg></button>
          <button className="searchbtn" id="openPal" onClick={openPal}><svg className="i"><use href="#i-search" /></svg><span className="t">{tr("Search papers, journals, manuscripts…")}</span><kbd>Ctrl K</kbd></button>
          <span className="pill model" id="modelPill" title="Active AI model"><svg className="i"><use href="#i-spark" /></svg><span className="mono" id="modelTx">{outage ? "offline" : "qwen2.5:14b"}</span></span>
          <button className="pill statusbtn" id="statusBtn" data-go="models" title="System status"><span className={"dot" + (outage ? " crit" : "")} id="statusDot"></span><span className="tx t" id="statusTx">{tr(outage ? "Ollama unavailable" : "All systems ready")}</span></button>
          <span className="sample t">{tr("Mockup · sample data")}</span>
          <button className="iconbtn" id="langBtn" aria-label="Language" title="English / العربية" onClick={toggleLang}><svg className="i"><use href="#i-globe" /></svg></button>
          <button className="iconbtn" id="themeBtn" aria-label="Theme" title={"Theme: " + theme} onClick={cycleTheme}><svg className="i"><use href={theme === "dark" ? "#i-moon" : "#i-sun"} /></svg></button>
          <button className="iconbtn bell" aria-label="Notifications" title="Notifications"><svg className="i"><use href="#i-bell" /></svg><span className="n">3</span></button>
          <span className="avatar" title="Account">MR</span>
        </header>

        <div className="body">
          <nav className="side" aria-label="Main">
            <div className="sec-label t">{tr("Workspace")}</div>
            <button className="nav" data-go="dashboard" title="Dashboard" aria-current={ac("dashboard")}><svg className="i"><use href="#i-dash" /></svg><span className="lbl t">{tr("Dashboard")}</span></button>
            <button className="nav" data-go="papers" title="Papers" aria-current={ac("papers")}><svg className="i"><use href="#i-paper" /></svg><span className="lbl t">{tr("Papers")}</span><span className="cnt">12</span></button>
            <button className="nav" data-go="journals" title="Journals" aria-current={ac("journals")}><svg className="i"><use href="#i-journal" /></svg><span className="lbl t">{tr("Journals")}</span><span className="cnt">4</span></button>
            <button className="nav" data-go="manuscript" title="Manuscripts" aria-current={ac("manuscript")}><svg className="i"><use href="#i-edit" /></svg><span className="lbl t">{tr("Manuscripts")}</span><span className="cnt">2</span></button>
            <div className="sec-label t">{tr("Review")}</div>
            <button className="nav" data-go="compliance" title="Compliance" aria-current={ac("compliance")}><svg className="i"><use href="#i-shield" /></svg><span className="lbl t">{tr("Compliance")}</span><span className="cnt crit">2</span></button>
            <button className="nav" data-go="reports" title="Reports" aria-current={ac("reports")}><svg className="i"><use href="#i-report" /></svg><span className="lbl t">{tr("Reports")}</span></button>
            <div className="grow"></div>
            <button className="nav" data-go="models" title="Models & System" aria-current={ac("models")}><svg className="i"><use href="#i-cpu" /></svg><span className="lbl t">{tr("Models & System")}</span></button>
          </nav>

          <main className="main" id="main" ref={mainRef}>
            <Outlet />
          </main>
        </div>
      </div>

      <div className="scrim" id="pal" hidden={!pal} onClick={(e) => { if (e.target === e.currentTarget) setPal(false); }}>
        <div className="pal" role="dialog" aria-modal="true" aria-label="Command palette">
          <input id="palIn" ref={palIn} type="text" placeholder={tr("Type a command or search")} autoComplete="off" value={q} onChange={(e) => { setQ(e.target.value); setIdx(0); }} onKeyDown={palKey} />
          <ul id="palList" ref={palList}>
            {shown.map((c, i) => (
              <li key={c[0]}>
                <button className={i === idx ? "act" : undefined} onClick={() => go(c[1])}><svg className="i"><use href={"#" + c[2]} /></svg><span>{tr(c[0])}</span></button>
              </li>
            ))}
          </ul>
          <div className="hint"><span><kbd>↑</kbd> <kbd>↓</kbd></span><span><kbd>Enter</kbd></span><span><kbd>Esc</kbd></span></div>
        </div>
      </div>
      <div className="toast" id="toast" role="status" hidden={!toastMsg}>{toastMsg}</div>
    </>
  );
}