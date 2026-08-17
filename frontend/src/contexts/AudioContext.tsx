import { createContext, useContext, useState, useRef, type ReactNode } from 'react';
import { getAudioUrl } from '../api/client';

interface AudioContextType {
  currentEpisodeId: string | null;
  currentTime: number;
  duration: number;
  isPlaying: boolean;
  isLoading: boolean;
  error: string | null;
  playFromTimestamp: (episodeId: string, startTime: number) => void;
  pause: () => void;
  play: () => void;
  seek: (time: number) => void;
  stop: () => void;
}

const AudioContext = createContext<AudioContextType | null>(null);

export function AudioProvider({ children }: { children: ReactNode }) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [currentEpisodeId, setCurrentEpisodeId] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const playFromTimestamp = (episodeId: string, startTime: number) => {
    const audio = audioRef.current;
    if (!audio) return;

    setError(null);
    setIsLoading(true);

    // If different episode, load new audio
    if (currentEpisodeId !== episodeId) {
      const audioUrl = getAudioUrl(episodeId);
      audio.src = audioUrl;
      setCurrentEpisodeId(episodeId);
      
      const handleLoaded = () => {
        audio.currentTime = startTime;
        audio.play();
        setIsLoading(false);
      };
      
      const handleError = () => {
        setError('Could not load audio for this episode.');
        setIsLoading(false);
      };

      audio.addEventListener('loadedmetadata', handleLoaded, { once: true });
      audio.addEventListener('error', handleError, { once: true });
    } else {
      // Same episode, just seek
      audio.currentTime = startTime;
      audio.play();
      setIsLoading(false);
    }
  };

  const pause = () => {
    audioRef.current?.pause();
  };

  const stop = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current.src = '';
    }
    setCurrentEpisodeId(null);
    setCurrentTime(0);
    setIsPlaying(false);
  };

  const play = () => {
    audioRef.current?.play();
  };

  const seek = (time: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = time;
    }
  };

  // Set up audio element event listeners
  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleDurationChange = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handlePlay = () => setIsPlaying(true);
  const handlePause = () => setIsPlaying(false);

  return (
    <AudioContext.Provider value={{
      currentEpisodeId,
      currentTime,
      duration,
      isPlaying,
      isLoading,
      error,
      playFromTimestamp,
      pause,
      play,
      seek,
      stop,
    }}>
      {children}
      <audio
        ref={audioRef}
        onTimeUpdate={handleTimeUpdate}
        onDurationChange={handleDurationChange}
        onPlay={handlePlay}
        onPause={handlePause}
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
