import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { chat, ApiError } from '../api/client';
import type { Message } from '../types/api';

interface ConversationContextType {
  sessionId: string;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  retry: () => void;
  newConversation: () => void;
}

const ConversationContext = createContext<ConversationContextType | null>(null);

function generateSessionId(): string {
  return crypto.randomUUID();
}

function readStorage<T>(key: string, fallback: T): T {
  try {
    const raw = sessionStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

function writeStorage(key: string, value: unknown) {
  try {
    sessionStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Storage can be unavailable (private mode); the conversation still works.
  }
}

export function ConversationProvider({ children }: { children: ReactNode }) {
  const [sessionId, setSessionId] = useState<string>(() => readStorage('fermi_session_id', generateSessionId()));
  const [messages, setMessages] = useState<Message[]>(() => readStorage<Message[]>('fermi_messages', []));
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => writeStorage('fermi_session_id', sessionId), [sessionId]);
  useEffect(() => writeStorage('fermi_messages', messages), [messages]);

  const ask = async (content: string, prior: Message[]) => {
    setIsLoading(true);
    setError(null);
    try {
      const history = prior.slice(-8).map(({ role, content }) => ({ role, content }));
      const response = await chat(sessionId, content, history);
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: response.response,
          sources: response.sources,
          intentUsed: response.intent_used,
          timestamp: Date.now(),
        },
      ]);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? "The companion hit an error while answering. Try again, or rephrase the question."
          : "Can't reach the companion. Check that the backend is running on port 8000, then try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (content: string) => {
    if (isLoading) return;
    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: 'user', content, timestamp: Date.now() },
    ]);
    await ask(content, messages);
  };

  // Re-ask the last question that didn't get an answer.
  const retry = () => {
    const last = messages[messages.length - 1];
    if (last?.role === 'user' && !isLoading) void ask(last.content, messages.slice(0, -1));
  };

  const newConversation = () => {
    setSessionId(generateSessionId());
    setMessages([]);
    setError(null);
  };

  return (
    <ConversationContext.Provider value={{
      sessionId,
      messages,
      isLoading,
      error,
      sendMessage,
      retry,
      newConversation,
    }}>
      {children}
    </ConversationContext.Provider>
  );
}

export function useConversation() {
  const context = useContext(ConversationContext);
  if (!context) {
    throw new Error('useConversation must be used within ConversationProvider');
  }
  return context;
}
