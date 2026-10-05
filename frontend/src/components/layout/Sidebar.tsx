import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { useI18n } from "../../context/I18nContext";

interface NavItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  count?: number;
  countClass?: string;
}

interface NavGroup {
  title: string;
  items: NavItem[];
}

const navGroups: NavGroup[] = [
  {
    title: "nav.group.work",
    items: [
      { id: "dashboard", label: "nav.dashboard", icon: "i-dash", path: "/" },
      { id: "papers", label: "nav.papers", icon: "i-paper", path: "/papers", count: 12 },
      { id: "journals", label: "nav.journals", icon: "i-journal", path: "/journals", count: 4 },
      { id: "manuscripts", label: "nav.manuscripts", icon: "i-edit", path: "/manuscripts", count: 2 },
    ],
  },
  {
    title: "nav.group.review",
    items: [
      { id: "compliance", label: "nav.compliance", icon: "i-shield", path: "/compliance", count: 2, countClass: "crit" },
      { id: "evaluations", label: "nav.evaluations", icon: "i-report", path: "/evaluations" },
      { id: "response-letters", label: "nav.response-letters", icon: "i-edit", path: "/response-letters" },
    ],
  },
];

export function Sidebar({ collapsed, onToggle }: { collapsed: boolean; onToggle: () => void }) {
  const { t } = useI18n();
  const location = useLocation();

  return (
    <nav className={"side" + (collapsed ? " collapsed" : "")} aria-label="Main">
      {navGroups.map((group) => (
        <div key={group.title}>
          {!collapsed && <div className="sec-label t">{t(group.title)}</div>}
          {group.items.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <button
                key={item.id}
                className={"nav" + (isActive ? " active" : "")}
                data-go={item.path.replace("/", "")}
                aria-current={isActive ? "page" : undefined}
                title={t(item.label)}
                onClick={() => { window.location.href = item.path; }}
              >
                <svg className="i">
                  <use href={"#" + item.icon} />
                </svg>
                {!collapsed && <span className="lbl t">{t(item.label)}</span>}
                {item.count !== undefined && (
                  <span className={"cnt" + (item.countClass ? " " + item.countClass : "")}>
                    {item.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      ))}
      <div className="grow" />
      {!collapsed && <div className="sec-label t">nav.group.system</div>}
      <button
        className="nav"
        data-go="models"
        title={t("nav.models")}
        onClick={() => { window.location.href = "/models"; }}
      >
        <svg className="i">
          <use href="#i-cpu" />
        </svg>
        {!collapsed && <span className="lbl t">{t("nav.models")}</span>}
      </button>
      <button
        className="nav"
        data-go="chat"
        title={t("nav.chat")}
        onClick={() => { window.location.href = "/chat"; }}
      >
        <svg className="i">
          <use href="#i-comment" />
        </svg>
        {!collapsed && <span className="lbl t">{t("nav.chat")}</span>}
      </button>
    </nav>
  );
}
