import type { ChatRequest, ChatResponse, Episode } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export async function chat(
  sessionId: string,
  message: string,
  history: ChatRequest['history'] = [],
): Promise<ChatResponse> {
  const request: ChatRequest = {
    session_id: sessionId,
    message,
    history,
  };

  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new ApiError(response.status, `Chat request failed: ${response.statusText}`);
  }

  return response.json();
}

export async function getEpisodes(): Promise<Episode[]> {
  const response = await fetch(`${API_BASE_URL}/episodes`);
  if (!response.ok) {
    throw new ApiError(response.status, `Episode list failed: ${response.statusText}`);
  }
  return response.json();
}

export function getAudioUrl(episodeId: string): string {
  return `${API_BASE_URL}/episodes/${episodeId}/audio`;
}
