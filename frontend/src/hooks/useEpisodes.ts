import { useEffect, useState } from 'react';
import { getEpisodes } from '../api/client';
import type { Episode } from '../types/api';

// One shared request for the whole app; the catalogue never changes at runtime.
let cache: Episode[] | null = null;
let inflight: Promise<Episode[]> | null = null;

function load(): Promise<Episode[]> {
  if (cache) return Promise.resolve(cache);
  if (!inflight) {
    inflight = getEpisodes()
      .then((episodes) => {
        cache = episodes;
        return episodes;
      })
      .catch((err) => {
        inflight = null; // allow a retry on next mount
        throw err;
      });
  }
  return inflight;
}

export function useEpisodes(): { episodes: Episode[]; failed: boolean } {
  const [episodes, setEpisodes] = useState<Episode[]>(cache ?? []);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    if (cache) return;
    let alive = true;
    load()
      .then((eps) => alive && setEpisodes(eps))
      .catch(() => alive && setFailed(true));
    return () => {
      alive = false;
    };
  }, []);

  return { episodes, failed };
}

export function findEpisode(episodes: Episode[], episodeId: string | null): Episode | undefined {
  if (!episodeId) return undefined;
  return episodes.find((e) => e.episode_id === episodeId);
}
