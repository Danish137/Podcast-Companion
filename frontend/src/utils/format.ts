/**
 * Format seconds to MM:SS
 */
export function formatTimestamp(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

/**
 * Format time range as MM:SS - MM:SS
 */
export function formatTimeRange(startSeconds: number, endSeconds: number): string {
  return `${formatTimestamp(startSeconds)} - ${formatTimestamp(endSeconds)}`;
}
