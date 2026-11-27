/**
 * Format seconds as M:SS (or H:MM:SS for long audio).
 */
export function formatTimestamp(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) seconds = 0;
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  const ss = s.toString().padStart(2, '0');
  return h > 0 ? `${h}:${m.toString().padStart(2, '0')}:${ss}` : `${m}:${ss}`;
}

/**
 * Format a time range as "M:SS–M:SS".
 */
export function formatTimeRange(startSeconds: number, endSeconds: number): string {
  return `${formatTimestamp(startSeconds)}–${formatTimestamp(endSeconds)}`;
}

/**
 * Restore readable accents the backend strips from titles (e.g. "Godel" -> "Gödel").
 */
export function displayTitle(title: string): string {
  return title.replace(/\bGodel/g, 'Gödel');
}

/**
 * Short label for an episode, used where space is tight: the part before the
 * first comma, cut at a word boundary.
 */
export function shortTitle(title: string, max = 24): string {
  const head = displayTitle(title).split(',')[0].trim();
  if (head.length <= max) return head;
  const cut = head.slice(0, max);
  return cut.slice(0, cut.lastIndexOf(' ') > 8 ? cut.lastIndexOf(' ') : max).trim() + '…';
}
