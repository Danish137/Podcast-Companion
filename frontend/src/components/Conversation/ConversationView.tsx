import { useConversation } from '../../contexts/ConversationContext';
import { EmptyState } from '../EmptyState';
import { MessageList } from './MessageList';
import { Composer } from './Composer';

export function ConversationView() {
  const { messages, isLoading, error } = useConversation();
  const started = messages.length > 0 || isLoading || error;

  return (
    <div className="flex-1 min-h-0 flex flex-col">
      {started ? <MessageList /> : <EmptyState />}
      <Composer />
    </div>
  );
}
