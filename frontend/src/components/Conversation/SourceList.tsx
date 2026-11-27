import { useAudio } from '../../contexts/AudioContext';
import type { SourceEvidence } from '../../types/api';
import { displayTitle, formatTimeRange } from '../../utils/format';
import { PauseIcon, PlayIcon } from '../icons';

/** The transcript passages an answer cites, each playable from its start. */
export function SourceList({ sources }: { sources: SourceEvidence[] }) {
  const { cue, isPlaying, playFromTimestamp, pause } = useAudio();

  return (
    <section className="mt-6" aria-label="Sources">
      <h3 className="text-[0.8rem] font-medium mb-2" style={{ color: 'var(--ink-soft)' }}>
        {sources.length === 1 ? 'Source' : `${sources.length} sources`} from the audio
      </h3>
      <ul
        className="overflow-hidden border"
        style={{ borderColor: 'var(--line)', borderRadius: 'var(--radius-row)', background: 'var(--surface)' }}
      >
        {sources.map((source, i) => {
          const active = cue?.episodeId === source.episode_id && cue.start === source.start_time;
          const playing = active && isPlaying;
          const title = displayTitle(source.episode_title);
          return (
            <li
              key={`${source.episode_id}-${source.start_time}`}
              style={{ borderTop: i === 0 ? 'none' : '1px solid var(--line)' }}
            >
              <button
                type="button"
                onClick={() => (playing ? pause() : playFromTimestamp(source.episode_id, source.start_time))}
                aria-label={playing ? `Pause ${title}` : `Play ${title} from ${formatTimeRange(source.start_time, source.end_time)}`}
                className="w-full text-left flex gap-3 px-4 py-3 transition-colors hover:bg-[var(--paper)]"
                style={{ background: active ? 'var(--accent-tint)' : undefined }}
              >
                <span
                  className="mt-0.5 flex-none w-7 h-7 rounded-full flex items-center justify-center"
                  style={{
                    background: active ? 'var(--accent)' : 'var(--accent-tint)',
                    color: active ? '#fff' : 'var(--accent)',
                  }}
                >
                  {playing ? <PauseIcon size={10} /> : <PlayIcon size={10} />}
                </span>
                <span className="min-w-0 flex-1">
                  <span className="flex flex-wrap items-baseline gap-x-2">
                    <span className="text-[0.9rem] font-medium" style={{ color: 'var(--ink)' }}>{title}</span>
                    <span className="text-[0.8rem] tabular" style={{ color: 'var(--ink-soft)' }}>
                      {formatTimeRange(source.start_time, source.end_time)}
                    </span>
                  </span>
                  {source.excerpt && (
                    <span
                      className="clamp-2 mt-1 text-[0.92rem] leading-relaxed"
                      style={{ color: 'var(--ink-soft)', fontFamily: 'var(--font-read)' }}
                    >
                      “{source.excerpt}”
                    </span>
                  )}
                </span>
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
