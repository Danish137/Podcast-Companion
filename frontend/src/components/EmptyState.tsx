import { useConversation } from '../contexts/ConversationContext';

export function EmptyState() {
  const { sendMessage } = useConversation();
  const examples = [
    "Explain special relativity simply",
    "Compare Einstein and Bell",
    "What covers information theory?",
    "What should I explore next?",
  ];

  return (
    <div className="flex-1 flex items-center justify-center px-6 py-8">
      <div className="max-w-3xl w-full space-y-8 text-center">
        {/* Hero Section */}
        <div className="space-y-6">
          <h1 
            className="text-display"
            style={{ color: 'var(--color-text-primary)' }}
          >
            Explore the ideas in
            <br />
            Fermi Podcast
          </h1>
          <p 
            className="text-lg max-w-2xl mx-auto"
            style={{ 
              color: 'var(--color-text-secondary)',
              lineHeight: '1.8'
            }}
          >
            Ask anything about the collection. Interact with the collection conversationally,
            follow the thread, and trace answers back to the original podcast audio.
          </p>
        </div>

        {/* Example Prompts */}
        <div className="space-y-4">
          <p 
            className="text-xs font-semibold uppercase tracking-wider"
            style={{ color: 'var(--color-text-tertiary)' }}
          >
            Try asking
          </p>
          <div className="grid gap-3 max-w-xl mx-auto">
            {examples.map((example, i) => (
              <button
                key={i}
                onClick={() => sendMessage(example)}
                className="text-left px-5 py-3 rounded-lg border transition-all cursor-pointer"
                style={{
                  backgroundColor: 'var(--color-bg-elevated)',
                  borderColor: 'var(--color-border-subtle)',
                  color: 'var(--color-text-secondary)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'var(--color-border-default)';
                  e.currentTarget.style.backgroundColor = 'var(--color-bg-subtle)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--color-border-subtle)';
                  e.currentTarget.style.backgroundColor = 'var(--color-bg-elevated)';
                }}
              >
                <span className="text-sm">{example}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
