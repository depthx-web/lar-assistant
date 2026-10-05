interface SkeletonProps {
  className?: string;
  lines?: number;
}

export function Skeleton({ className, lines = 1 }: SkeletonProps) {
  if (lines > 1) {
    return (
      <div>
        {Array.from({ length: lines }).map((_, i) => (
          <div key={i} className={'skel' + (className ? ' '+ className : '')} style={{ marginBottom: i < lines - 1 ? 8 : 0 }} />
        ))}
      </div>
    );
  }
  return <div className={'skel' + (className ? ' '+ className : '')} />;
}
