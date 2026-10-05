interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div style={{ textAlign: 'center', padding: '48px 0' }}>
      {icon && <div style={{ marginBottom: 16 }}>{icon}</div>}
      <p style={{ color: 'var(--ink-2)' }}>{title}</p>
      {description && <p style={{ fontSize: 12.5, color: 'var(--ink-3)', marginTop: 8 }}>{description}</p>}
      {action && <div style={{ marginTop: 24 }}>{action}</div>}
    </div>
  );
}
