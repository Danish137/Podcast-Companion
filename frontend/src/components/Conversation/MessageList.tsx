import { useEffect, useRef } from 'react';
import { useConversation } from '../../contexts/ConversationContext';
import { UserMessage } from './UserMessage';
import { AssistantMessage } from './AssistantMessage';
import { Wave } from '../icons';

function ThinkingRow() {
  return (
    <div className="flex items-center gap-2.5 rise" role="status" style={{ color: 'var(--accent)' }}>
      <Wave />
      <span className="text-[0.9rem]" style={{ color: 'var(--ink-soft)' }}>
        Searching the episodes and checking the evidence…
      </span>
    </div>
  );
}

function ErrorRow({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div
      role="alert"
      className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 text-[0.9rem] rise"
      style={{ background: 'var(--danger-tint)', color: 'var(--danger)', borderRadius: 'var(--radius-row)' }}
    >
      <span>{message}</span>
      <button
        type="button"
        onClick={onRetry}
        className="font-medium px-3 py-1 rounded-lg border"
        style={{ borderColor: 'currentColor', background: 'transparent', color: 'inherit' }}
      >
        Try again
      </button>
    </div>
  );
}

export function MessageList() {
  const { messages, isLoading, error, retry } = useConversation();
  const scrollRef = useRef<HTMLDivElement>(null);
  const endRef = useRef<HTMLDivElement>(null);

  // When the learner asks something, bring their question to the top of the view
  // so the answer appears right beneath it.
  useEffect(() => {
    const last = messages[messages.length - 1];
    if (!last) return;
    if (last.role === 'user') {
      document.getElementById(`msg-${last.id}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [messages]);

  // Keep a new error message in view.
  useEffect(() => {
    if (error) endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [error]);

  return (
    <div ref={scrollRef} className="flex-1 min-h-0 overflow-y-auto" role="log" aria-live="polite" aria-relevant="additions">
      <div className="max-w-[46rem] mx-auto px-4 sm:px-6 pt-8 pb-10 flex flex-col gap-8">
        {messages.map((message) => (
          <div key={message.id} id={`msg-${message.id}`} className="scroll-mt-6">
            {message.role === 'user' ? (
              <UserMessage content={message.content} />
            ) : (
              <AssistantMessage content={message.content} sources={message.sources} />
            )}
          </div>
        ))}
        {isLoading && <ThinkingRow />}
        {error && !isLoading && <ErrorRow message={error} onRetry={retry} />}
        {/* Leaves room so the last question can scroll to the top while its answer loads */}
        <div ref={endRef} aria-hidden="true" style={{ minHeight: isLoading ? '50vh' : 0 }} />
      </div>
    </div>
  );
}
