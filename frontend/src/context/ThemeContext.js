import { jsx as _jsx } from "react/jsx-runtime";
import React from "react";
import { createContext, useContext, useState, useCallback } from "react";
const ThemeContext = createContext({
    theme: "light",
    resolved: "light",
    setTheme: () => { },
});
export function ThemeProvider({ children }) {
    const [theme, setThemeState] = useState(() => {
        const saved = localStorage.getItem("lara-theme");
        return (saved === "dark" || saved === "light" || saved === "system") ? saved : "light";
    });
    const resolved = React.useMemo(() => {
        if (theme === "dark")
            return "dark";
        if (theme === "light")
            return "light";
        return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }, [theme]);
    const setTheme = useCallback((t) => {
        setThemeState(t);
        localStorage.setItem("lara-theme", t);
    }, []);
    React.useEffect(() => {
        document.documentElement.classList.toggle("dark", resolved === "dark");
    }, [resolved]);
    return (_jsx(ThemeContext.Provider, { value: { theme, resolved, setTheme }, children: children }));
}
export function useTheme() {
    return useContext(ThemeContext);
}
