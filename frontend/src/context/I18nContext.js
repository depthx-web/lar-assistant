import { jsx as _jsx } from "react/jsx-runtime";
import { createContext, useContext, useEffect } from "react";
import { useTranslation } from "react-i18next";
const I18nContext = createContext(null);
export function I18nProvider({ children }) {
    const { t, i18n } = useTranslation();
    const setLang = (lng) => i18n.changeLanguage(lng);
    const dir = i18n.language === "ar" ? "rtl" : "ltr";
    useEffect(() => {
        document.documentElement.setAttribute("dir", dir);
        document.documentElement.setAttribute("lang", i18n.language);
    }, [dir, i18n.language]);
    return (_jsx(I18nContext.Provider, { value: { t, i18n, lang: i18n.language, setLang, dir }, children: children }));
}
export function useI18n() {
    const ctx = useContext(I18nContext);
    if (!ctx)
        throw new Error("useI18n must be used within I18nProvider");
    return ctx;
}
