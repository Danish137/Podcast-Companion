import { useConversation } from '../contexts/ConversationContext';
import { useAudio } from '../contexts/AudioContext';

export function Layout({ children }: { children: React.ReactNode }) {
  const { newConversation, messages } = useConversation();
  const { stop: stopAudio } = useAudio();

  return (
    <div className="h-screen flex flex-col" style={{ backgroundColor: 'var(--color-bg-primary)' }}>
      {/* Header */}
      <header 
        className="sticky top-0 z-10 border-b"
        style={{ 
          backgroundColor: 'var(--color-bg-elevated)',
          borderColor: 'var(--color-border-subtle)'
        }}
      >
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/fermi-mark.png" alt="Fermi Logo" className="w-7 h-7" />
            <h1 className="text-brand" style={{ color: 'var(--color-text-primary)' }}>
              Fermi Podcast Companion
            </h1>
          </div>
          {messages.length > 0 && (
            <button
              onClick={() => {
                newConversation();
                stopAudio();
              }}
              className="px-4 py-2 text-sm font-medium rounded-lg transition-all"
              style={{
                color: 'var(--color-text-secondary)',
                backgroundColor: 'transparent'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--color-bg-hover)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              New conversation
            </button>
          )}
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {children}
      </main>
    </div>
  );
}
