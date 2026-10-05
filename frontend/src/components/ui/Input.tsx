interface InputProps {
  label?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onKeyDown?: (e: React.KeyboardEvent<HTMLInputElement>) => void;
  placeholder?: string;
  type?: string;
  helper?: string;
  className?: string;
}

export function Input({ label, value, onChange, placeholder, type = 'text', helper, className }: InputProps) {
  return (
    <div className={className}>
      {label && <label className='t' style={{ display: 'block', fontSize: 12.5, color: 'var(--ink-2)', marginBottom: 4 }}>{label}</label>}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className='field'
        style={{ width: '100%' }}
      />
      {helper && <span className='faint' style={{ fontSize: 11.5, marginTop: 4, display: 'block' }}>{helper}</span>}
    </div>
  );
}
