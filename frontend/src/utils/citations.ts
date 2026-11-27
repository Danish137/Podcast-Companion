import type { Episode, SourceEvidence } from '../types/api';
import { shortTitle } from './format';

/**
 * Citations in answers look like "[Episode Title, 14:30]". Titles can contain
 * commas ("How Black Holes Radiate, Hawking 1975"), and the model sometimes
 * writes ranges, several timestamps, or several "Title, MM:SS" pairs in one
 * bracket. Mirrors parse_citations in src/companion.py.
 */
const BRACKET = /\[([^[\]]+)\]/g;
const TIME_TOKEN = /^\d{1,3}:\d{2}(?:\s*[-–]\s*\d{1,3}:\d{2})?$/;

/** Split a bracket's inside into (title, seconds) pairs; null if it isn't a citation. */
function parseBracket(inner: string): { title: string; seconds: number }[] | null {
  const pairs: { title: string; seconds: number }[] = [];
  let titleParts: string[] = [];
  let lastWasTime = false;
  for (const token of inner.split(/[,;]/).map((t) => t.trim()).filter(Boolean)) {
    if (TIME_TOKEN.test(token)) {
      if (!titleParts.length) return null;
      const seconds = toSeconds(token);
      if (seconds !== null) pairs.push({ title: titleParts.join(', '), seconds });
      lastWasTime = true;
    } else {
      if (lastWasTime) titleParts = [];
      lastWasTime = false;
      titleParts.push(token);
    }
  }
  return pairs.length ? pairs : null;
}

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
  for (const match of markdown.matchAll(BRACKET)) {
    for (const pair of parseBracket(match[1]) ?? []) {
      const ep = resolve(lookup, pair.title);
      if (ep) citedIds.add(ep.id);
    }
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
        .replace(BRACKET, (whole, inner: string) => {
          const pairs = parseBracket(inner);
          if (!pairs) return whole;
          const out: string[] = [];
          let resolvedAny = false;
          for (const { title, seconds } of pairs) {
            const ep = resolve(lookup, title);
            const m = Math.floor(seconds / 60);
            const label = `${m}:${String(seconds % 60).padStart(2, '0')}`;
            if (!ep) {
              out.push(`[${title}, ${label}]`); // unknown episode: keep as plain text
              continue;
            }
            resolvedAny = true;
            const key = `${ep.id}-${seconds}`;
            if (seen.has(key)) continue;
            seen.add(key);
            const text = showTitles ? `${shortTitle(ep.title)} ${label}` : label;
            out.push(`[${text.replace(/[[\]]/g, '')}](${CITE_HREF_PREFIX}${ep.id}-${seconds})`);
          }
          if (!resolvedAny) return whole;
          return out.length ? out.join(' ') : DROPPED;
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
