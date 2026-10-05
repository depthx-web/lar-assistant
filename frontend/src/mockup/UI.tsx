import { createContext, useCallback, useContext, useEffect, useRef, useState, ReactNode } from "react";
import i18n from "../i18n/config";
import { AR } from "./ar";

export type Theme = "system" | "light" | "dark";
type Lang = "en" | "ar";

interface UIState {
  lang: Lang;
  toggleLang: () => void;
  theme: Theme;
  cycleTheme: () => void;
  outage: boolean;
  setOutage: (v: boolean) => void;
  toastMsg: string;
  toast: (m: string) => void;
  tr: (s: string) => string;
}

const Ctx = createContext<UIState | null>(null);

function load(k: string) { try { return localStorage.getItem(k); } catch { return null; } }
function store(k: string, v: string) { try { localStorage.setItem(k, v); } catch { /* ignore */ } }

export function UIProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>(() => (load("ara-lang") === "ar" ? "ar" : "en"));
  const [theme, setTheme] = useState<Theme>(() => {
    const t = load("ara-theme");
    return t === "light" || t === "dark" ? t : "system";
  });
  const [outage, setOutage] = useState(false);
  const [toastMsg, setToastMsg] = useState("");
  const timer = useRef<number | undefined>(undefined);

  const tr = useCallback((s: string) => (lang === "ar" ? AR[s] || s : s), [lang]);

  const toast = useCallback((m: string) => {
    setToastMsg(m);
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => setToastMsg(""), 1800);
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    root.lang = lang;
    root.dir = lang === "ar" ? "rtl" : "ltr";
    if (i18n.language !== lang) i18n.changeLanguage(lang);
  }, [lang]);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "system") root.removeAttribute("data-theme");
    else root.setAttribute("data-theme", theme);
  }, [theme]);

  const toggleLang = () => {
    const n: Lang = lang === "en" ? "ar" : "en";
    store("ara-lang", n);
    setLang(n);
  };
  const cycleTheme = () => {
    const n: Theme = theme === "system" ? "light" : theme === "light" ? "dark" : "system";
    store("ara-theme", n);
    setTheme(n);
    toast((lang === "ar" ? AR["Theme"] : "Theme") + ": " + n);
  };

  return (
    <Ctx.Provider value={{ lang, toggleLang, theme, cycleTheme, outage, setOutage, toastMsg, toast, tr }}>
      {children}
    </Ctx.Provider>
  );
}

export function useUI() {
  const c = useContext(Ctx);
  if (!c) throw new Error("useUI must be used within UIProvider");
  return c;
}