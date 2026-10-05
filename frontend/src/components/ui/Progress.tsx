interface ProgressProps {
  value?: number;
  max?: number;
  className?: string;
  showLabel?: boolean;
  size?: 'sm' | 'md';
}

export function Progress({ value = 0, max = 100, className, showLabel, size = 'md' }: ProgressProps) {
  const pct = Math.round((value / max) * 100);
  const height = size === 'sm' ? 4 : 6;
  return (
    <div className={'prog' + (className ? ' '+ className : '')} style={{ height }}>
      <i style={{ width: pct + '%' }} />
      {showLabel && <span className='v' style={{ fontSize: 11, marginTop: 4 }}>{pct + '%'}</span>}
    </div>
  );
}
