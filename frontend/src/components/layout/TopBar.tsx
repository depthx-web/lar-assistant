import { useEffect, useState } from "react";
import { useI18n } from "../../context/I18nContext";
import { CommandPalette } from "./CommandPalette";
import { useTheme } from "../../context/ThemeContext";

export function TopBar({
  onToggleSidebar,
  collapsed,
}: {
  onToggleSidebar: () => void;
  collapsed: boolean;
}) {
  const { t, lang, setLang } = useI18n();
  const { resolved, setTheme } = useTheme();
  const [palOpen, setPalOpen] = useState(false);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setPalOpen(true);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  return (
    <>
      <header className="top">
        <button
          className="iconbtn"
          onClick={onToggleSidebar}
          aria-label="Toggle sidebar"
          title={t("common.toggle_sidebar") || "Toggle sidebar"}
        >
          <svg className="i">
            <use href="#i-panel" />
          </svg>
        </button>
        <div className="brand">
          <span className="mark" aria-hidden="true">§</span>
          <span className="nm t">Academic Research Assistant</span>
        </div>
        <button className="proj" aria-label="Current project">
          <span className="faint t">Project</span>
          <b>Hippocampal atrophy in MCI</b>
          <svg className="i">
            <use href="#i-down" />
          </svg>
        </button>
        <button
          className="searchbtn"
          onClick={() => setPalOpen(true)}
          id="openPal"
        >
          <svg className="i">
            <use href="#i-search" />
          </svg>
          <span className="t">Search papers, journals, manuscripts…</span>
          <kbd>Ctrl K</kbd>
        </button>
        <span className="pill model" title="Active AI model">
          <svg className="i">
            <use href="#i-spark" />
          </svg>
          <span className="mono">qwen2.5:14b</span>
        </span>
        <button className="pill statusbtn" title="System status">
          <span className="dot" id="statusDot" />
          <span className="tx t" id="statusTx">All systems ready</span>
        </button>
        <span className="sample t">Mockup · sample data</span>
        <button
          className="iconbtn"
          onClick={() => setLang(lang === "ar" ? "en" : "ar")}
          aria-label="Language"
          title="English / العربية"
        >
          <svg className="i">
            <use href="#i-globe" />
          </svg>
        </button>
        <button
          className="iconbtn"
          onClick={() => setTheme(resolved === "dark" ? "light" : "dark")}
          aria-label="Theme"
          title="Light / Dark / System"
        >
          <svg className="i">
            <use href={resolved === "dark" ? "#i-sun" : "#i-moon"} />
          </svg>
        </button>
        <button
          className="iconbtn bell"
          aria-label="Notifications"
          title={t("common.notifications")}
        >
          <svg className="i">
            <use href="#i-bell" />
          </svg>
          <span className="n">3</span>
        </button>
        <span className="avatar" title="Account">
          MR
        </span>
      </header>
      <CommandPalette open={palOpen} onClose={() => setPalOpen(false)} />
    </>
  );
}