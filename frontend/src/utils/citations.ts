import type { Episode, SourceEvidence } from '../types/api';
import { shortTitle } from './format';

/**
 * Citations in answers look like "[Episode Title, 14:30]". Titles can contain
 * commas ("How Black Holes Radiate, Hawking 1975") and the model sometimes
 * writes ranges or several timestamps in one bracket. Mirrors CITATION_PATTERN
 * in src/companion.py.
 */
const CITATION =
  /\[([^[\]]+?),\s*(\d{1,3}:\d{2}(?:\s*[-–]\s*\d{1,3}:\d{2})?(?:\s*,\s*\d{1,3}:\d{2}(?:\s*[-–]\s*\d{1,3}:\d{2})?)*)\]/g;

export const CITE_HREF_PREFIX = '#cite-';

export function normalizeTitle(title: string): string {
  return title
    .normalize('NFKD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '');
}

type TitleLookup = { id: string; norm: string; title: string }[];

function buildLookup(episodes: Episode[], sources: SourceEvidence[] = []): TitleLookup {
  const seen = new Map<string, { id: string; norm: string; title: string }>();
  for (const e of episodes) seen.set(e.episode_id, { id: e.episode_id, norm: normalizeTitle(e.episode_title), title: e.episode_title });
  for (const s of sources) {
    if (!seen.has(s.episode_id)) {
      seen.set(s.episode_id, { id: s.episode_id, norm: normalizeTitle(s.episode_title), title: s.episode_title });
    }
  }
  return [...seen.values()];
}

function resolve(lookup: TitleLookup, citedTitle: string) {
  const norm = normalizeTitle(citedTitle);
  if (!norm) return undefined;
  return (
    lookup.find((e) => e.norm === norm) ??
    lookup.find((e) => e.norm.startsWith(norm) || norm.startsWith(e.norm))
  );
}

function toSeconds(part: string): number | null {
  const m = part.match(/(\d{1,3}):(\d{2})/);
  return m ? Number(m[1]) * 60 + Number(m[2]) : null;
}

/**
 * Rewrite citations into markdown links ("[label](#cite-ep14-1230)") that the
 * answer renderer turns into playable timestamp chips. Citations to unknown
 * episodes are left as plain text.
 */
export function linkCitations(markdown: string, episodes: Episode[], sources: SourceEvidence[] = []): string {
  const lookup = buildLookup(episodes, sources);

  // First pass: which episodes are cited? One episode -> chips show only times.
  const citedIds = new Set<string>();
  for (const match of markdown.matchAll(CITATION)) {
    const ep = resolve(lookup, match[1]);
    if (ep) citedIds.add(ep.id);
  }
  const showTitles = citedIds.size > 1;
  const DROPPED = '\u0000';

  // The model often repeats the same citation after every sentence. Show each
  // timestamp once per line (a paragraph or list item); later repeats are dropped.
  return markdown
    .split('\n')
    .map((line) => {
      const seen = new Set<string>();
      return line
        .replace(CITATION, (whole, title: string, times: string) => {
          const ep = resolve(lookup, title);
          if (!ep) return whole;
          const chips = times
            .split(',')
            .map((part) => toSeconds(part))
            .filter((s): s is number => s !== null)
            .filter((seconds) => {
              const key = `${ep.id}-${seconds}`;
              if (seen.has(key)) return false;
              seen.add(key);
              return true;
            })
            .map((seconds) => {
              const m = Math.floor(seconds / 60);
              const label = `${m}:${String(seconds % 60).padStart(2, '0')}`;
              const text = showTitles ? `${shortTitle(ep.title)} ${label}` : label;
              return `[${text.replace(/[[\]]/g, '')}](${CITE_HREF_PREFIX}${ep.id}-${seconds})`;
            });
          return chips.length ? chips.join(' ') : DROPPED;
        })
        .replace(/\s*\u0000/g, '');
    })
    .join('\n');
}

export function parseCiteHref(href: string | undefined): { episodeId: string; seconds: number } | null {
  if (!href || !href.startsWith(CITE_HREF_PREFIX)) return null;
  const m = href.slice(CITE_HREF_PREFIX.length).match(/^(.+)-(\d+)$/);
  return m ? { episodeId: m[1], seconds: Number(m[2]) } : null;
}
