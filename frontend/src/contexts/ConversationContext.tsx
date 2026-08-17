import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { chat, ApiError } from '../api/client';
import type { Message } from '../types/api';

interface ConversationContextType {
  sessionId: string;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  newConversation: () => void;
}

const ConversationContext = createContext<ConversationContextType | null>(null);

function generateSessionId(): string {
  return crypto.randomUUID();
}

export function ConversationProvider({ children }: { children: ReactNode }) {
  const [sessionId, setSessionId] = useState(() => {
    return sessionStorage.getItem('fermi_session_id') || generateSessionId();
  });
  const [messages, setMessages] = useState<Message[]>(() => {
    const saved = sessionStorage.getItem('fermi_messages');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        return [];
      }
    }
    return [];
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sync to sessionStorage
  useEffect(() => {
    sessionStorage.setItem('fermi_session_id', sessionId);
  }, [sessionId]);

  useEffect(() => {
    sessionStorage.setItem('fermi_messages', JSON.stringify(messages));
  }, [messages]);

  const sendMessage = async (content: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: Date.now(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await chat(sessionId, content);
      
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.response,
        sources: response.sources,
        intentUsed: response.intent_used,
        timestamp: Date.now(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = err instanceof ApiError 
        ? 'Something went wrong while getting that explanation.' 
        : 'Network error. Please check your connection.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
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
      newConversation 
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
