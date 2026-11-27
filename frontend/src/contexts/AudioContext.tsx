import { createContext, useContext, useState, useRef, type ReactNode } from 'react';
import { getAudioUrl } from '../api/client';

/** The timestamp the learner asked to hear, so its chip/source row can show it's playing. */
export interface AudioCue {
  episodeId: string;
  start: number;
}

interface AudioContextType {
  currentEpisodeId: string | null;
  cue: AudioCue | null;
  currentTime: number;
  duration: number;
  isPlaying: boolean;
  isLoading: boolean;
  error: string | null;
  playFromTimestamp: (episodeId: string, startTime: number) => void;
  pause: () => void;
  play: () => void;
  seek: (time: number) => void;
  skip: (deltaSeconds: number) => void;
  stop: () => void;
}

const AudioContext = createContext<AudioContextType | null>(null);

export function AudioProvider({ children }: { children: ReactNode }) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [currentEpisodeId, setCurrentEpisodeId] = useState<string | null>(null);
  const [cue, setCue] = useState<AudioCue | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Listeners for the load in progress, so they can be removed before the next
  // load or a stop. Leftover 'error' listeners otherwise fire on unrelated events.
  const pendingListenersRef = useRef<{ loaded: () => void; error: () => void } | null>(null);

  const clearPendingListeners = () => {
    const audio = audioRef.current;
    const pending = pendingListenersRef.current;
    if (audio && pending) {
      audio.removeEventListener('loadedmetadata', pending.loaded);
      audio.removeEventListener('error', pending.error);
    }
    pendingListenersRef.current = null;
  };

  const safePlay = (audio: HTMLAudioElement) => {
    audio.play().catch(() => {
      // Autoplay or interrupted-play rejections are not load failures.
    });
  };

  const playFromTimestamp = (episodeId: string, startTime: number) => {
    const audio = audioRef.current;
    if (!audio) return;

    setError(null);
    setCue({ episodeId, start: startTime });

    // Same episode already loaded: just seek.
    if (currentEpisodeId === episodeId && !error && !pendingListenersRef.current) {
      audio.currentTime = startTime;
      setCurrentTime(startTime);
      safePlay(audio);
      return;
    }

    setIsLoading(true);
    clearPendingListeners();

    const handleLoaded = () => {
      pendingListenersRef.current = null;
      audio.removeEventListener('error', handleError);
      audio.currentTime = startTime;
      setCurrentTime(startTime);
      safePlay(audio);
      setIsLoading(false);
    };

    const handleError = () => {
      pendingListenersRef.current = null;
      audio.removeEventListener('loadedmetadata', handleLoaded);
      setError("This episode's audio couldn't be loaded. Check that the backend is running, then try again.");
      setIsLoading(false);
      setIsPlaying(false);
    };

    pendingListenersRef.current = { loaded: handleLoaded, error: handleError };
    audio.addEventListener('loadedmetadata', handleLoaded, { once: true });
    audio.addEventListener('error', handleError, { once: true });

    setCurrentTime(startTime);
    setDuration(0);
    audio.src = getAudioUrl(episodeId);
    setCurrentEpisodeId(episodeId);
  };

  const pause = () => {
    audioRef.current?.pause();
  };

  const stop = () => {
    clearPendingListeners();
    if (audioRef.current) {
      audioRef.current.pause();
      // Setting src = '' makes the browser try to load the page URL and fire
      // an 'error' event; removing the attribute unloads cleanly instead.
      audioRef.current.removeAttribute('src');
      audioRef.current.load();
    }
    setCurrentEpisodeId(null);
    setCue(null);
    setCurrentTime(0);
    setDuration(0);
    setIsPlaying(false);
    setIsLoading(false);
    setError(null);
  };

  const play = () => {
    if (audioRef.current) safePlay(audioRef.current);
  };

  const seek = (time: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = time;
      setCurrentTime(time);
    }
  };

  const skip = (deltaSeconds: number) => {
    const audio = audioRef.current;
    if (!audio) return;
    const max = Number.isFinite(audio.duration) ? audio.duration : Infinity;
    seek(Math.min(Math.max(0, audio.currentTime + deltaSeconds), max));
  };

  return (
    <AudioContext.Provider value={{
      currentEpisodeId,
      cue,
      currentTime,
      duration,
      isPlaying,
      isLoading,
      error,
      playFromTimestamp,
      pause,
      play,
      seek,
      skip,
      stop,
    }}>
      {children}
      <audio
        ref={audioRef}
        preload="metadata"
        onTimeUpdate={() => audioRef.current && setCurrentTime(audioRef.current.currentTime)}
        onDurationChange={() => audioRef.current && setDuration(audioRef.current.duration)}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onEnded={() => setIsPlaying(false)}
        onWaiting={() => setIsLoading(true)}
        onPlaying={() => setIsLoading(false)}
      />
    </AudioContext.Provider>
  );
}

export function useAudio() {
  const context = useContext(AudioContext);
  if (!context) {
    throw new Error('useAudio must be used within AudioProvider');
  }
  return context;
}
