import { useEffect, useRef } from 'react';
import { useConversation } from '../../contexts/ConversationContext';
import { UserMessage } from './UserMessage';
import { AssistantMessage } from './AssistantMessage';

export function MessageList() {
  const { messages } = useConversation();
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to the start of the last interaction
  useEffect(() => {
    if (messages.length === 0) return;
    
    // Find the last user message and scroll it to the top of the view
    const lastUserMsg = [...messages].reverse().find(m => m.role === 'user');
    if (lastUserMsg) {
      const el = document.getElementById(`msg-${lastUserMsg.id}`);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  }, [messages.length]);

  return (
    <div
      className="flex-1 overflow-y-auto px-6 py-12"
      role="log"
      aria-live="polite"
      aria-relevant="additions"
      style={{ backgroundColor: 'var(--color-bg-primary)' }}
    >
      <div className="max-w-3xl mx-auto space-y-6">
        {messages.map((message) => (
          <div key={message.id} id={`msg-${message.id}`}>
            {message.role === 'user' ? (
              <UserMessage content={message.content} />
            ) : (
              <AssistantMessage
                content={message.content}
                sources={message.sources}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
