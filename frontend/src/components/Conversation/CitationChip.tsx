import type { ReactNode } from 'react';
import { useAudio } from '../../contexts/AudioContext';
import { useEpisodes, findEpisode } from '../../hooks/useEpisodes';
import { displayTitle, formatTimestamp } from '../../utils/format';
import { PlayIcon, Wave } from '../icons';

interface CitationChipProps {
  episodeId: string;
  seconds: number;
  children: ReactNode;
}

/** Inline timestamp in an answer. Clicking plays the episode from that moment. */
export function CitationChip({ episodeId, seconds, children }: CitationChipProps) {
  const { cue, isPlaying, playFromTimestamp, pause } = useAudio();
  const { episodes } = useEpisodes();
  const title = displayTitle(findEpisode(episodes, episodeId)?.episode_title ?? 'this episode');

  const isCued = cue?.episodeId === episodeId && cue.start === seconds;
  const label = isCued && isPlaying
    ? `Pause ${title} at ${formatTimestamp(seconds)}`
    : `Play ${title} from ${formatTimestamp(seconds)}`;

  return (
    <button
      type="button"
      className="cite"
      data-active={isCued}
      title={`${title}, ${formatTimestamp(seconds)}`}
      aria-label={label}
      onClick={() => (isCued && isPlaying ? pause() : playFromTimestamp(episodeId, seconds))}
    >
      {isCued ? <Wave paused={!isPlaying} /> : <PlayIcon size={8} />}
      <span>{children}</span>
    </button>
  );
}
