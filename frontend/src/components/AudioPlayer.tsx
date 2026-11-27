import { useAudio } from '../contexts/AudioContext';
import { useEpisodes, findEpisode } from '../hooks/useEpisodes';
import { displayTitle, formatTimestamp } from '../utils/format';
import { BackIcon, CloseIcon, PauseIcon, PlayIcon, Spinner } from './icons';

/** Compact player that sits on top of the composer inside the bottom dock. */
export function AudioPlayer() {
  const {
    currentEpisodeId, currentTime, duration, isPlaying, isLoading, error,
    pause, play, seek, skip, stop,
  } = useAudio();
  const { episodes } = useEpisodes();

  if (!currentEpisodeId && !error) return null;

  const episode = findEpisode(episodes, currentEpisodeId);
  const title = episode ? displayTitle(episode.episode_title) : 'Episode audio';
  const total = duration || episode?.duration_seconds || 0;
  const pct = total ? Math.min(100, (currentTime / total) * 100) : 0;

  if (error) {
    return (
      <div className="flex items-center gap-3 px-4 py-2.5 text-[0.85rem]" role="alert" style={{ color: 'var(--danger)' }}>
        <span className="flex-1">{error}</span>
        <button type="button" onClick={stop} aria-label="Dismiss" className="p-1.5 rounded-md hover:bg-[var(--paper)]">
          <CloseIcon />
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-3 px-3 sm:px-4 py-2.5" aria-label="Episode audio player" role="region">
      <button
        type="button"
        onClick={isPlaying ? pause : play}
        aria-label={isPlaying ? 'Pause' : 'Play'}
        className="flex-none w-9 h-9 rounded-full flex items-center justify-center transition-colors"
        style={{ background: 'var(--accent)', color: '#fff' }}
      >
        {isLoading ? <Spinner /> : isPlaying ? <PauseIcon /> : <PlayIcon />}
      </button>

      <button
        type="button"
        onClick={() => skip(-15)}
        aria-label="Back 15 seconds"
        title="Back 15 seconds"
        className="flex-none hidden sm:flex w-8 h-8 rounded-full items-center justify-center hover:bg-[var(--paper)]"
        style={{ color: 'var(--ink-soft)' }}
      >
        <BackIcon />
      </button>

      <div className="min-w-0 flex-1">
        <div className="flex items-baseline justify-between gap-3">
          <span className="truncate text-[0.85rem] font-medium" style={{ color: 'var(--ink)' }}>{title}</span>
          <span className="flex-none text-[0.75rem] tabular" style={{ color: 'var(--ink-soft)' }}>
            {formatTimestamp(currentTime)} / {formatTimestamp(total)}
          </span>
        </div>
        <input
          type="range"
          className="scrub block"
          min={0}
          max={total || 0}
          step={1}
          value={Math.min(currentTime, total || 0)}
          onChange={(e) => seek(Number(e.target.value))}
          disabled={!total}
          aria-label="Seek"
          aria-valuetext={`${formatTimestamp(currentTime)} of ${formatTimestamp(total)}`}
          style={{ ['--pct' as string]: `${pct}%` }}
        />
      </div>

      <button
        type="button"
        onClick={stop}
        aria-label="Close player"
        className="flex-none w-8 h-8 rounded-full flex items-center justify-center hover:bg-[var(--paper)]"
        style={{ color: 'var(--ink-soft)' }}
      >
        <CloseIcon />
      </button>
    </div>
  );
}
