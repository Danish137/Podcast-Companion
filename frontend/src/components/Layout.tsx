import { useConversation } from '../contexts/ConversationContext';
import { useAudio } from '../contexts/AudioContext';
import { PlusIcon } from './icons';

export function Layout({ children }: { children: React.ReactNode }) {
  const { newConversation, messages, isLoading } = useConversation();
  const { stop: stopAudio } = useAudio();

  return (
    <div className="h-full flex flex-col" style={{ background: 'var(--paper)' }}>
      <header className="flex-none border-b" style={{ borderColor: 'var(--line)', background: 'var(--surface)' }}>
        <div className="max-w-[46rem] mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-4">
          <div className="flex items-center gap-2.5 min-w-0">
            <img src="/fermi-mark.png" alt="" className="w-7 h-7 rounded-md flex-none" />
            <h1 className="m-0 text-[1rem] font-semibold truncate" style={{ color: 'var(--ink)' }}>
              Fermi Companion
              <span className="hidden sm:inline font-normal" style={{ color: 'var(--ink-faint)' }}>
                {'  '}for the Great Papers podcast
              </span>
            </h1>
          </div>
          {messages.length > 0 && (
            <button
              type="button"
              onClick={() => {
                newConversation();
                stopAudio();
              }}
              disabled={isLoading}
              className="flex-none flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-[0.85rem] font-medium transition-colors hover:bg-[var(--paper)] disabled:opacity-50"
              style={{ borderColor: 'var(--line-strong)', color: 'var(--ink)' }}
            >
              <PlusIcon />
              New conversation
            </button>
          )}
        </div>
      </header>

      <main className="flex-1 min-h-0 flex flex-col">{children}</main>
    </div>
  );
}
