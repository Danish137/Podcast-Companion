import type { ChatRequest, ChatResponse } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export async function chat(sessionId: string, message: string): Promise<ChatResponse> {
  const request: ChatRequest = {
    session_id: sessionId,
    message,
  };

  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new ApiError(
      response.status,
      `Chat request failed: ${response.statusText}`
    );
  }

  return response.json();
}

export function getAudioUrl(episodeId: string): string {
  return `${API_BASE_URL}/episodes/${episodeId}/audio`;
}
