import fs from 'fs';

const sidebarContent = `import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { cn } from "../ui/cn";
import {
  LayoutDashboard, FileText, BookOpen, ScrollText,
  CheckCircle, Cpu, Settings, MessageSquare,
  ChevronLeft, ChevronRight, Moon, Sun, Languages,
  Star, PenTool, Tags, GitCompare, Download, Send, Lightbulb
} from "lucide-react";
import { useI18n } from "../../context/I18nContext";
import { useTheme } from "../../context/ThemeContext";

interface NavItem {
  id: string;
  label: string;
  icon: any;
  path: string;
  shortcut: string;
}

interface NavGroup {
  title: string;
  items: NavItem[];
}

const navGroups: NavGroup[] = [
  {
    title: "nav.group.work",
    items: [
      { id: "dashboard",  label: "nav.dashboard",  icon: LayoutDashboard, path: "/",          shortcut: "D" },
      { id: "papers",     label: "nav.papers",     icon: BookOpen,        path: "/papers",      shortcut: "P" },
      { id: "journals",   label: "nav.journals",   icon: FileText,        path: "/journals",    shortcut: "J" },
      { id: "manuscripts",label: "nav.manuscripts",icon: ScrollText,      path: "/manuscripts", shortcut: "M" },
    ],
  },
  {
    title: "nav.group.analysis",
    items: [
      { id: "evaluations",     label: "nav.evaluations",     icon: Star,          path: "/evaluations",    shortcut: "E" },
      { id: "compliance",      label: "nav.compliance",      icon: CheckCircle,   path: "/compliance",     shortcut: "C" },
      { id: "response-letters",label: "nav.response-letters",icon: PenTool,       path: "/response-letters",shortcut: "R" },
      { id: "improvements",    label: "nav.improvements",    icon: Lightbulb,     path: "/improvements",   shortcut: "I" },
    ],
  },
  {
    title: "nav.group.tools",
    items: [
      { id: "tags-comments",  label: "nav.tags-comments",  icon: Tags,          path: "/tags-comments",  shortcut: "T" },
      { id: "diff",           label: "nav.diff",           icon: GitCompare,    path: "/diff",           shortcut: "D" },
      { id: "exports",        label: "nav.exports",        icon: Download,      path: "/exports",        shortcut: "X" },
      { id: "submission",     label: "nav.submission",     icon: Send,          path: "/submission",     shortcut: "S" },
    ],
  },
  {
    title: "nav.group.system",
    items: [
      { id: "models",     label: "nav.models",     icon: Cpu,    path: "/models",     shortcut: "O" },
      { id: "status",     label: "nav.status",     icon: Settings, path: "/status",     shortcut: "S" },
      { id: "chat",       label: "nav.chat",       icon: MessageSquare, path: "/chat",       shortcut: "K" },
    ],
  },
};

export function Sidebar({ collapsed, onToggle }: { collapsed: boolean; onToggle: () => void }) {
  const { t, lang, setLang } = useI18n();
  const { resolved, setTheme } = useTheme();
  const location = useLocation();

  return (
    <div className={cn(
      "flex flex-col bg-surface border-r border-border transition-all duration-300",
      collapsed ? "w-16" : "w-64"
    )}>
      <div className="flex items-center justify-between p-4 border-b border-border">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center shadow-sm">
              <span className="text-white font-bold text-sm">LA</span>
            </div>
            <div>
              <p className="font-semibold text-text leading-tight">{t("app.name")}</p>
              <p className="text-xs text-text-muted leading-tight">{t("app.subtitle")}</p>
            </div>
          </div>
        )}
        {collapsed && (
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center mx-auto shadow-sm">
            <span className="text-white font-bold text-sm">LA</span>
          </div>
        )}
        <button
          onClick={onToggle}
          className="p-1.5 rounded-lg text-text-faint hover:text-text hover:bg-surface-2 transition-colors"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto p-2">
        <div className="space-y-4">
          {navGroups.map((group) => (
            <div key={group.title}>
              {!collapsed && (
                <p className="px-3 py-1 text-[10px] font-semibold uppercase tracking-wider text-text-faint">
                  {t(group.title)}
                </p>
              )}
              <div className="space-y-0.5">
                {group.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path;
                  return (
                    <Link
                      key={item.id}
                      to={item.path}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-150",
                        isActive
                          ? "bg-primary/10 text-primary font-medium"
                          : "text-text-muted hover:text-text hover:bg-surface-2"
                      )}
                    >
                      <Icon className={cn("w-5 h-5 shrink-0", isActive && "text-primary")} />
                      {!collapsed && (
                        <>
                          <span className="flex-1 truncate">{t(item.label)}</span>
                          <span className="text-[10px] text-text-faint tabular-nums">{item.shortcut}</span>
                        </>
                      )}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </nav>

      <div className="p-2 border-t border-border space-y-1">
        <button
          onClick={() => setTheme(resolved === "dark" ? "light" : "dark")}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-text-muted hover:text-text hover:bg-surface-2 transition-colors"
        >
          {resolved === "dark" ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          {!collapsed && <span className="flex-1 text-left">{resolved === "dark" ? t("theme.light") : t("theme.dark")}</span>}
        </button>
        <button
          onClick={() => setLang(lang === "en" ? "ar" : "en")}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-text-muted hover:text-text hover:bg-surface-2 transition-colors"
        >
          <Languages className="w-5 h-5" />
          {!collapsed && <span className="flex-1 text-left">{lang === "en" ? "العربية" : "English"}</span>}
        </button>
      </div>
    </div>
  );
}

