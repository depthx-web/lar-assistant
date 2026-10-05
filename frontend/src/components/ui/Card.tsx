interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  subtitle?: string | React.ReactNode;
  action?: React.ReactNode;
}

export function Card({ children, className, title, subtitle, action }: CardProps) {
  return (
    <div className={"box" + (className ? " " + className : "")}>
      {(title || subtitle || action) && (
        <header>
          <div>
            {title && <h2>{title}</h2>}
            {subtitle && <p className="faint">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </header>
      )}
      <div className="in">{children}</div>
    </div>
  );
}

interface PageHeaderProps {
  title: string;
  subtitle?: string | React.ReactNode;
  action?: React.ReactNode;
}

export function PageHeader({ title, subtitle, action }: PageHeaderProps) {
  return (
    <div className="pagehead">
      <div>
        <h1>{title}</h1>
        {subtitle && <p className="sub">{subtitle}</p>}
      </div>
      {action && <div className="actions">{action}</div>}
    </div>
  );
}
