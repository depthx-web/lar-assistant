import { createContext, useContext, ReactNode, useEffect } from "react";
import { useTranslation } from "react-i18next";

const I18nContext = createContext<{
  t: ReturnType<typeof useTranslation>["t"];
  i18n: ReturnType<typeof useTranslation>["i18n"];
  lang: string;
  setLang: (lng: string) => void;
  dir: "ltr" | "rtl";
} | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const { t, i18n } = useTranslation();
  const setLang = (lng: string) => i18n.changeLanguage(lng);
  const dir: "ltr" | "rtl" = i18n.language === "ar" ? "rtl" : "ltr";

  useEffect(() => {
    document.documentElement.setAttribute("dir", dir);
    document.documentElement.setAttribute("lang", i18n.language);
  }, [dir, i18n.language]);

  return (
    <I18nContext.Provider value={{ t, i18n, lang: i18n.language, setLang, dir }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
}

