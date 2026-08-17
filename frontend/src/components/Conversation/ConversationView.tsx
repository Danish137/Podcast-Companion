import { useConversation } from '../../contexts/ConversationContext';
import { EmptyState } from '../EmptyState';
import { MessageList } from './MessageList';
import { Composer } from './Composer';
import { AudioPlayer } from '../AudioPlayer';

export function ConversationView() {
  const { messages, error } = useConversation();

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col overflow-hidden">
        <EmptyState />
        <Composer />
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <MessageList />
      
      {error && (
        <div 
          className="px-6 py-4 border-t"
          style={{
            backgroundColor: '#fef2f2',
            borderColor: '#fecaca'
          }}
        >
          <div className="max-w-3xl mx-auto flex items-center justify-between">
            <p className="text-sm" style={{ color: '#991b1b' }}>
              {error}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="text-sm font-medium px-3 py-1 rounded transition-colors"
              style={{ color: '#dc2626' }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#fee2e2';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              Retry
            </button>
          </div>
        </div>
      )}
      
      <AudioPlayer />
      <Composer />
    </div>
  );
}
