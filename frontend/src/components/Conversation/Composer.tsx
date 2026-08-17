import { useState, useRef, useEffect, type KeyboardEvent } from 'react';
import { useConversation } from '../../contexts/ConversationContext';

export function Composer() {
  const { sendMessage, isLoading } = useConversation();
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleSubmit = async () => {
    const message = input.trim();
    if (!message || isLoading) return;

    setInput('');
    await sendMessage(message);
    
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div 
      className="border-t px-2 py-2"
      style={{
        backgroundColor: 'var(--color-bg-elevated)',
        borderColor: 'var(--color-border-subtle)'
      }}
    >
      <div className="max-w-3xl mx-auto">
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            placeholder="What do you want to understand?"
            aria-label="Your question"
            className="w-full resize-none px-5 py-4 pr-14 border rounded-xl focus:outline-none transition-all min-h-[64px] max-h-[200px]"
            style={{
              backgroundColor: 'var(--color-bg-elevated)',
              borderColor: 'var(--color-border-default)',
              color: 'var(--color-text-primary)',
              fontSize: 'var(--text-base)',
              lineHeight: '1.5'
            }}
            onFocus={(e) => {
              e.currentTarget.style.borderColor = 'var(--color-accent)';
              e.currentTarget.style.boxShadow = '0 0 0 3px var(--color-accent-subtle)';
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = 'var(--color-border-default)';
              e.currentTarget.style.boxShadow = 'none';
            }}
            rows={1}
          />
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || isLoading}
            aria-label="Send message"
            className="absolute right-3 bottom-3 w-10 h-10 flex items-center justify-center rounded-lg transition-all focus:outline-none"
            style={{
              backgroundColor: input.trim() && !isLoading ? 'var(--color-accent)' : 'var(--color-bg-subtle)',
              color: input.trim() && !isLoading ? 'white' : 'var(--color-text-tertiary)'
            }}
            onMouseEnter={(e) => {
              if (input.trim() && !isLoading) {
                e.currentTarget.style.backgroundColor = 'var(--color-accent-hover)';
              }
            }}
            onMouseLeave={(e) => {
              if (input.trim() && !isLoading) {
                e.currentTarget.style.backgroundColor = 'var(--color-accent)';
              }
            }}
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M3 10L17 10M17 10L11 4M17 10L11 16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>
        {isLoading && (
          <div className="mt-3 flex items-center gap-2" style={{ color: 'var(--color-text-tertiary)' }}>
            <div className="flex gap-1">
              <div className="w-1.5 h-1.5 rounded-full animate-bounce" style={{ backgroundColor: 'currentColor' }}></div>
              <div className="w-1.5 h-1.5 rounded-full animate-bounce" style={{ backgroundColor: 'currentColor', animationDelay: '0.15s' }}></div>
              <div className="w-1.5 h-1.5 rounded-full animate-bounce" style={{ backgroundColor: 'currentColor', animationDelay: '0.3s' }}></div>
            </div>
            <span className="text-sm font-medium">Processing...</span>
          </div>
        )}
      </div>
    </div>
  );
}
