type IconProps = { size?: number; className?: string };

export function PlayIcon({ size = 12, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 12 12" fill="currentColor" aria-hidden="true" className={className}>
      <path d="M3 1.8v8.4c0 .4.45.65.8.43l6.6-4.2a.5.5 0 0 0 0-.86L3.8 1.37A.5.5 0 0 0 3 1.8z" />
    </svg>
  );
}

export function PauseIcon({ size = 12, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 12 12" fill="currentColor" aria-hidden="true" className={className}>
      <rect x="2.5" y="1.5" width="2.6" height="9" rx="0.8" />
      <rect x="6.9" y="1.5" width="2.6" height="9" rx="0.8" />
    </svg>
  );
}

export function CloseIcon({ size = 14, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true" className={className}>
      <path d="M3.5 3.5l7 7M10.5 3.5l-7 7" />
    </svg>
  );
}

export function SendIcon({ size = 16, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" className={className}>
      <path d="M8 13V3M3.5 7.5L8 3l4.5 4.5" />
    </svg>
  );
}

export function BackIcon({ size = 16, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" className={className}>
      <path d="M3 8a5 5 0 1 0 1.6-3.7" />
      <path d="M3 2.5v2.6h2.6" />
    </svg>
  );
}

export function PlusIcon({ size = 14, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true" className={className}>
      <path d="M7 2.5v9M2.5 7h9" />
    </svg>
  );
}

/** Four animated bars; pauses when audio is paused. */
export function Wave({ paused = false }: { paused?: boolean }) {
  return (
    <span className={`wave${paused ? ' paused' : ''}`} aria-hidden="true">
      <i /><i /><i /><i />
    </span>
  );
}

export function Spinner({ size = 14 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" className="animate-spin" aria-hidden="true">
      <circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" strokeOpacity="0.25" strokeWidth="2" />
      <path d="M14 8a6 6 0 0 0-6-6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}
