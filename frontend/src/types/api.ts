export interface SourceEvidence {
  episode_id: string;
  episode_title: string;
  start_time: number;  // seconds
  end_time: number;    // seconds
  excerpt?: string;
}

export interface ChatResponse {
  response: string;
  intent_used: string;
  sources: SourceEvidence[];
}

export interface ChatRequest {
  session_id: string;
  message: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceEvidence[];
  intentUsed?: string;
  timestamp: number;
}
