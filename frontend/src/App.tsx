import { ConversationProvider } from './contexts/ConversationContext';
import { AudioProvider } from './contexts/AudioContext';
import { Layout } from './components/Layout';
import { ConversationView } from './components/Conversation/ConversationView';

function App() {
  return (
    <ConversationProvider>
      <AudioProvider>
        <Layout>
          <ConversationView />
        </Layout>
      </AudioProvider>
    </ConversationProvider>
  );
}

export default App;
