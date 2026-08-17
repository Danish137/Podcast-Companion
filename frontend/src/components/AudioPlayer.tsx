import { useAudio } from '../contexts/AudioContext';
import { formatTimestamp } from '../utils/format';

export function AudioPlayer() {
  const {
    currentEpisodeId,
    currentTime,
    duration,
    isPlaying,
    isLoading,
    error,
    pause,
    play,
    seek,
    stop,
  } = useAudio();

  if (!currentEpisodeId && !error) {
    return null;
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    seek(Number(e.target.value));
  };

  return (
    <div 
      className="border-t px-2 py-2"
      style={{
        backgroundColor: 'var(--color-bg-elevated)',
        borderColor: 'var(--color-border-subtle)'
      }}
    >
      <div className="max-w-3xl mx-auto">
        {error ? (
          <div className="text-sm" style={{ color: '#ef4444' }}>{error}</div>
        ) : (
          <div className="space-y-3">
            <div className="flex items-center gap-4">
              <button
                onClick={isPlaying ? pause : play}
                disabled={isLoading}
                aria-label={isPlaying ? 'Pause' : 'Play'}
                className="flex-shrink-0 w-11 h-11 flex items-center justify-center rounded-full transition-all focus:outline-none"
                style={{
                  backgroundColor: 'white',
                  color: '#0a0a0a'
                }}
                onMouseEnter={(e) => {
                  if (!isLoading) {
                    e.currentTarget.style.backgroundColor = '#f5f5f5';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'white';
                }}
              >
                {isLoading ? (
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                ) : isPlaying ? (
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M6 4h3v12H6V4zm5 0h3v12h-3V4z" />
                  </svg>
                ) : (
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M6 4l10 6-10 6V4z" />
                  </svg>
                )}
              </button>

              <div className="flex-1 flex items-center gap-3">
                <span 
                  className="text-xs font-mono tabular-nums"
                  style={{ color: '#a3a3a3' }}
                >
                  {formatTimestamp(currentTime)}
                </span>
                <div className="flex-1 relative h-1 rounded-full" style={{ backgroundColor: '#404040' }}>
                  <input
                    type="range"
                    min="0"
                    max={duration || 0}
                    value={currentTime}
                    onChange={handleSeek}
                    disabled={isLoading}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
                    aria-label="Seek audio"
                  />
                  <div 
                    className="absolute left-0 top-0 h-full rounded-full transition-all"
                    style={{
                      width: `${duration ? (currentTime / duration) * 100 : 0}%`,
                      backgroundColor: 'var(--color-accent)'
                    }}
                  />
                </div>
                <span 
                  className="text-xs font-mono tabular-nums"
                  style={{ color: '#a3a3a3' }}
                >
                  {formatTimestamp(duration)}
                </span>
              </div>
              <button
                onClick={stop}
                className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-full transition-all focus:outline-none hover:bg-gray-100"
                style={{ color: '#737373' }}
                aria-label="Close audio"
              >
                <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>

            <div className="text-xs" style={{ color: '#737373' }}>
              Episode audio player
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
