import { formatTimeRange, formatTimestamp } from '../../utils/format';
import { useAudio } from '../../contexts/AudioContext';
import type { SourceEvidence } from '../../types/api';

interface SourceCardProps {
  source: SourceEvidence;
}

export function SourceCard({ source }: SourceCardProps) {
  const { playFromTimestamp } = useAudio();

  const handleListen = () => {
    playFromTimestamp(source.episode_id, source.start_time);
  };

  return (
    <div 
      className="rounded-lg border px-5 py-4 space-y-3"
      style={{
        backgroundColor: 'var(--color-bg-elevated)',
        borderColor: 'var(--color-border-subtle)'
      }}
    >
      <div 
        className="text-xs font-semibold uppercase tracking-wider"
        style={{ color: 'var(--color-text-tertiary)' }}
      >
        Source
      </div>
      
      <div className="space-y-1">
        <h4 
          className="font-semibold"
          style={{ 
            color: 'var(--color-text-primary)',
            fontSize: 'var(--text-base)'
          }}
        >
          {source.episode_title}
        </h4>
        <p 
          className="text-sm font-mono"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          {formatTimeRange(source.start_time, source.end_time)}
        </p>
      </div>

      {source.excerpt && (
        <p 
          className="text-sm leading-relaxed"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          {source.excerpt}
        </p>
      )}

      <button
        onClick={handleListen}
        className="flex items-center gap-2 text-sm font-medium transition-colors rounded px-3 py-2 -ml-3"
        style={{ color: 'var(--color-accent)' }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = 'var(--color-accent-subtle)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'transparent';
        }}
      >
        <svg width="14" height="14" viewBox="0 0 14 14" fill="currentColor">
          <path d="M3 2.5v9l8-4.5-8-4.5z" />
        </svg>
        <span>Listen from {formatTimestamp(source.start_time)}</span>
      </button>
    </div>
  );
}
