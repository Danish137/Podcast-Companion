import { useState, useRef, useEffect, type KeyboardEvent } from 'react';
import { useConversation } from '../../contexts/ConversationContext';
import { useAudio } from '../../contexts/AudioContext';
import { AudioPlayer } from '../AudioPlayer';
import { SendIcon } from '../icons';

/**
 * Bottom dock: the audio player (when something is playing) and the question
 * box live in one floating card, so playback never pushes between the
 * conversation and the input.
 */
export function Composer() {
  const { sendMessage, isLoading, messages } = useConversation();
  const { currentEpisodeId, error: audioError } = useAudio();
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const playerOpen = Boolean(currentEpisodeId || audioError);
  const canSend = input.trim().length > 0 && !isLoading;

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 180)}px`;
    }
  }, [input]);

  // Return focus to the box once an answer arrives.
  useEffect(() => {
    if (!isLoading) textareaRef.current?.focus({ preventScroll: true });
  }, [isLoading]);

  const handleSubmit = () => {
    const message = input.trim();
    if (!message || isLoading) return;
    setInput('');
    void sendMessage(message);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div
      className="flex-none px-3 sm:px-6 pb-3 sm:pb-4 pt-2"
      style={{ background: 'linear-gradient(to bottom, transparent, var(--paper) 30%)' }}
    >
      <div className="max-w-[46rem] mx-auto">
        <div
          className="overflow-hidden border transition-shadow focus-within:border-[var(--accent)]"
          style={{
            background: 'var(--surface)',
            borderColor: 'var(--line)',
            borderRadius: 'var(--radius-dock)',
            boxShadow: 'var(--dock-shadow)',
          }}
        >
          {playerOpen && (
            <div style={{ borderBottom: '1px solid var(--line)' }}>
              <AudioPlayer />
            </div>
          )}

          <div className="flex items-end gap-2 p-2 pl-4">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={messages.length ? 'Ask a follow-up, or say what didn’t click' : 'Ask about any idea in the episodes'}
              aria-label="Your question"
              rows={1}
              className="flex-1 resize-none bg-transparent border-0 outline-none py-2 text-[1rem] leading-6 max-h-[180px]"
              style={{ color: 'var(--ink)' }}
            />
            <button
              type="button"
              onClick={handleSubmit}
              disabled={!canSend}
              aria-label="Send question"
              className="flex-none w-9 h-9 rounded-full flex items-center justify-center transition-colors"
              style={{
                background: canSend ? 'var(--accent)' : 'var(--paper)',
                color: canSend ? '#fff' : 'var(--ink-faint)',
              }}
            >
              <SendIcon />
            </button>
          </div>
        </div>
        <p className="mt-2 text-center text-[0.75rem]" style={{ color: 'var(--ink-faint)' }}>
          Answers come only from the podcast audio. Click a timestamp to hear the original.
        </p>
      </div>
    </div>
  );
}
