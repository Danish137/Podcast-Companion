# Frontend Implementation Design

## Overview

This design document specifies the technical implementation of the Fermi Companion frontend—a conversation-first web interface for learning about landmark scientific papers through grounded dialogue with the podcast collection.

**Product Identity:**  
An intelligent learning companion, NOT a podcast browser or episode catalogue.

**Core Loop:**  
ASK → UNDERSTAND → VERIFY → EXPLORE

**Key Principle:**  
Discovery is conversational. The learner asks questions; the companion identifies relevant material automatically.

---

## Architecture

### Technology Stack

**Framework:** React 18.2+ with TypeScript 5.0+  
**Build Tool:** Vite 5.0+  
**Styling:** Tailwind CSS 3.4+  
**Markdown:** react-markdown 9.0+  
**HTTP Client:** Native fetch API  
**State Management:** React Context API + useState (no Redux/Zustand)

**Rationale:**
- React: Industry standard, excellent TypeScript support, component ecosystem
- Vite: Fast dev server, optimal HMR, zero-config
- Tailwind: Rapid prototyping, utility-first, no runtime CSS-in-JS overhead
- Native fetch: Sufficient for this scope, no axios dependency needed
- Context API: Simple state sharing without heavy state management library

### Project Structure

```
frontend/
├── public/
├── src/
│   ├── api/
│   │   └── client.ts              # Centralized API layer
│   ├── components/
│   │   ├── Conversation/
│   │   │   ├── ConversationView.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── UserMessage.tsx
│   │   │   ├── AssistantMessage.tsx
│   │   │   ├── SourceCard.tsx
│   │   │   └── Composer.tsx
│   │   ├── EmptyState.tsx
│   │   ├── AudioPlayer.tsx
│   │   ├── Layout.tsx
│   │   └── ErrorBoundary.tsx
│   ├── contexts/
│   │   ├── ConversationContext.tsx
│   │   └── AudioContext.tsx
│   ├── hooks/
│   │   ├── useChat.ts
│   │   ├── useSession.ts
│   │   └── useAudio.ts
│   ├── types/
│   │   └── api.ts
│   ├── utils/
│   │   └── format.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

### Component Hierarchy

```
App
├── ErrorBoundary
│   └── ConversationContext.Provider
│       └── AudioContext.Provider
│           ├── Layout
│           │   ├── Header
│           │   └── ConversationView
│           │       ├── EmptyState (conditional)
│           │       ├── MessageList
│           │       │   ├── UserMessage
│           │       │   └── AssistantMessage
│           │       │       ├── ResponseText (react-markdown)
│           │       │       └── SourceCard[]
│           │       └── Composer
│           │           ├── Textarea
│           │           ├── SendButton
│           │           └── LoadingIndicator
│           └── AudioPlayer (fixed position)
```

**No Episode Browser:** No EpisodeList, EpisodeCard, or catalogue components.

---

## Components and Interfaces

### Core Components

#### App.tsx
- Root component
- Provides contexts (Conversation, Audio)
- Wraps in ErrorBoundary
- Renders Layout

#### Layout.tsx
- Header with title and "New Conversation" action
- Main content area for ConversationView
- Fixed audio player at bottom
- Responsive container

#### EmptyState.tsx
**Shown when:** No messages in conversation

**Content:**
```
FERMI COMPANION

Explore the ideas behind landmark scientific papers.

Ask a question, understand a concept,
then trace the answer back to the audio.

[Input field]

Try asking:
• "Explain special relativity simply"
• "Which material covers information theory?"
• "Compare Einstein and Bell"
• "Does the collection discuss string theory?"
```

**Styling:** Centered, calm, editorial, clear typography

#### ConversationView.tsx
- Container for conversation
- Conditionally renders EmptyState or MessageList + Composer
- Manages scroll behavior
- Auto-scroll to bottom on new messages

#### MessageList.tsx
- Scrollable container
- Maps over messages array
- Renders UserMessage or AssistantMessage based on role
- Maintains scroll position
- Simple reverse-chronological layout

#### UserMessage.tsx
**Props:** `{ content: string }`

**Renders:**
- User's question text
- Right-aligned
- Distinct visual treatment (subtle background)

#### AssistantMessage.tsx
**Props:** `{ content: string, sources: Source[], intentUsed: string }`

**Renders:**
- Markdown-formatted response via react-markdown
- Array of SourceCard components below response
- Optional contextual follow-up suggestions (if time permits)
- Intent-aware styling (subtle differences for COMPARE vs EXPLAIN)

**Note:** Does NOT show intent_used label to user (internal only)

#### SourceCard.tsx
**Props:** 
```typescript
{
  episodeId: string;
  episodeTitle: string;
  startTime: number;
  endTime: number;
  excerpt?: string;
}
```

**Renders:**
```
SOURCE

Great Papers 01
Einstein's Special Relativity

18:42 – 19:31

[excerpt text if available]

▶ Listen from 18:42
```

**Behavior:**
- Click "Listen from..." button → triggers audio playback via AudioContext
- Compact card design with clear hierarchy
- Episode badge (title only, no browse link)
- Timestamp range formatted as MM:SS
- Excerpt in subdued text (max 200 chars)

**Does NOT show:**
- Similarity scores
- Retrieval confidence
- Internal metadata
- Episode selection controls

#### Composer.tsx
**State:** `message: string`, `isLoading: boolean`

**Renders:**
- Textarea (auto-resizing)
- Send button
- Loading indicator (when waiting for response)

**Behavior:**
- Enter to submit (Shift+Enter for newline)
- Disabled during loading
- Clear input after successful send
- Focus management
- Accessible labels

#### AudioPlayer.tsx
**Global player, fixed at bottom of viewport**

**State (via AudioContext):**
```typescript
{
  currentEpisodeId: string | null;
  currentTime: number;
  duration: number;
  isPlaying: boolean;
  isLoading: boolean;
}
```

**Renders:**
- Compact bar (not full podcast player UI)
- Episode title (current)
- Play/pause button
- Seek slider
- Current time / total duration (MM:SS format)
- Loading spinner when fetching audio

**Behavior:**
- Load audio when SourceCard "Listen from..." clicked
- Seek to specified timestamp
- Standard HTML5 audio controls behavior
- HTTP range request support (browser native)
- Error handling for failed audio loads

**Does NOT include:**
- Playlists
- Speed controls
- Download buttons
- Complex podcast player features

---

## Data Models

### TypeScript Interfaces

#### API Response Types

```typescript
// POST /chat response
interface ChatResponse {
  response: string;           // Markdown text
  intent_used: string;        // EXPLAIN | COMPARE | DISCOVER | UNSUPPORTED
  sources: SourceEvidence[];  // Structured sources (NEW)
}

interface SourceEvidence {
  episode_id: string;         // "ep01"
  episode_title: string;      // "Einstein's Special Relativity"
  start_time: number;         // 690.0 (seconds)
  end_time: number;           // 780.0 (seconds)
  excerpt?: string;           // Optional text excerpt
}
```

#### Frontend State Types

```typescript
interface Message {
  id: string;                 // UUID
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceEvidence[]; // Only for assistant messages
  intentUsed?: string;        // Only for assistant messages
  timestamp: number;
}

interface ConversationState {
  sessionId: string;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

interface AudioState {
  currentEpisodeId: string | null;
  audioUrl: string | null;
  currentTime: number;
  duration: number;
  isPlaying: boolean;
  isLoading: boolean;
  error: string | null;
}
```

---

## API Contract

### Backend Endpoints (Required Modifications)

#### Modified: POST /chat

**Current Implementation (verified):**
```python
class ChatResponse(BaseModel):
    response: str
    intent_used: str
```

**Required Change:**
```python
class SourceEvidence(BaseModel):
    episode_id: str
    episode_title: str
    start_time: float
    end_time: float
    excerpt: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    intent_used: str
    sources: List[SourceEvidence] = []  # NEW
```

**Implementation Notes:**
- Existing backend already has `state.last_retrieved_evidence` with chunk objects
- These chunks contain: episode_id, episode_title, start_time, end_time, text
- Simply map these to SourceEvidence objects and return
- Keep markdown citations for backward compatibility if needed
- Format timestamps remain in seconds (frontend converts to MM:SS)

#### New: GET /episodes/{episode_id}/audio

**Purpose:** Serve audio files for source verification

**Request:**
```
GET /episodes/ep01/audio
Range: bytes=0-1000000
```

**Response:**
```
200 OK
Content-Type: audio/mpeg
Content-Length: 50000000
Accept-Ranges: bytes
Content-Range: bytes 0-49999999/50000000

[binary audio data]
```

**Implementation:**
```python
from fastapi import HTTPException
from fastapi.responses import FileResponse

@app.get("/episodes/{episode_id}/audio")
async def get_episode_audio(episode_id: str):
    # Load manifest
    manifest_path = METADATA_DIR / "episode_manifest.json"
    with open(manifest_path) as f:
        episodes = json.load(f)
    
    # Find episode
    episode = next((ep for ep in episodes if ep["episode_id"] == episode_id), None)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    # Map to audio file
    audio_path = PODCAST_DIR / episode["filename"]
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    # Return with range support
    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
        filename=episode["filename"]
    )
```

**Security:**
- Validates episode_id against manifest (no arbitrary file access)
- Only serves files in PODCAST_DIR
- Rejects path traversal attempts

#### Optional: GET /episodes

**Decision:** Only implement if genuinely needed for source display.

**Current Assessment:** NOT needed because:
- Sources come with full metadata in `/chat` response
- No episode browsing UI
- Discovery is conversational

**If needed later:**
```python
@app.get("/episodes")
async def get_episodes():
    manifest_path = METADATA_DIR / "episode_manifest.json"
    with open(manifest_path) as f:
        episodes = json.load(f)
    return {"episodes": episodes}
```

#### CORS Configuration

**Only if frontend served on different port during development**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Frontend API Client

### api/client.ts

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface ChatRequest {
  session_id: string;
  message: string;
}

interface ChatResponse {
  response: string;
  intent_used: string;
  sources: SourceEvidence[];
}

interface SourceEvidence {
  episode_id: string;
  episode_title: string;
  start_time: number;
  end_time: number;
  excerpt?: string;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export async function chat(sessionId: string, message: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message }),
  });

  if (!response.ok) {
    throw new ApiError(response.status, `Chat request failed: ${response.statusText}`);
  }

  return response.json();
}

export function getAudioUrl(episodeId: string): string {
  return `${API_BASE_URL}/episodes/${episodeId}/audio`;
}
```

**Notes:**
- Centralized API calls
- Typed interfaces matching backend
- Error handling with custom ApiError
- Environment variable for API base URL
- Audio URL construction (no separate fetch needed - let <audio> handle it)

---

## State Management

### ConversationContext

**Provides:**
- `sessionId: string`
- `messages: Message[]`
- `isLoading: boolean`
- `error: string | null`
- `sendMessage: (content: string) => Promise<void>`
- `newConversation: () => void`

**Implementation:**
```typescript
export const ConversationContext = createContext<ConversationContextType | null>(null);

export function ConversationProvider({ children }: { children: ReactNode }) {
  const [sessionId, setSessionId] = useState(() => generateSessionId());
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: Date.now(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await chat(sessionId, content);
      
      // Add assistant message
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.response,
        sources: response.sources,
        intentUsed: response.intent_used,
        timestamp: Date.now(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong');
    } finally {
      setIsLoading(false);
    }
  };

  const newConversation = () => {
    setSessionId(generateSessionId());
    setMessages([]);
    setError(null);
  };

  return (
    <ConversationContext.Provider value={{ 
      sessionId, 
      messages, 
      isLoading, 
      error, 
      sendMessage, 
      newConversation 
    }}>
      {children}
    </ConversationContext.Provider>
  );
}

function generateSessionId(): string {
  return crypto.randomUUID();
}
```

### AudioContext

**Provides:**
- `playFromTimestamp: (episodeId: string, startTime: number) => void`
- `pause: () => void`
- `currentEpisodeId: string | null`
- `isPlaying: boolean`
- `currentTime: number`
- `duration: number`

**Implementation:**
```typescript
export function AudioProvider({ children }: { children: ReactNode }) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [state, setState] = useState<AudioState>({
    currentEpisodeId: null,
    currentTime: 0,
    duration: 0,
    isPlaying: false,
    isLoading: false,
    error: null,
  });

  const playFromTimestamp = (episodeId: string, startTime: number) => {
    const audio = audioRef.current;
    if (!audio) return;

    const audioUrl = getAudioUrl(episodeId);
    
    // If different episode, load new audio
    if (state.currentEpisodeId !== episodeId) {
      audio.src = audioUrl;
      audio.load();
    }

    // Seek to timestamp and play
    audio.addEventListener('loadedmetadata', () => {
      audio.currentTime = startTime;
      audio.play();
    }, { once: true });

    setState(prev => ({ ...prev, currentEpisodeId: episodeId, isPlaying: true }));
  };

  return (
    <AudioContext.Provider value={{ ...state, playFromTimestamp, pause }}>
      {children}
      <audio ref={audioRef} />
    </AudioContext.Provider>
  );
}
```

---

## Error Handling

### Types of Errors

1. **Network errors** (no connection to backend)
2. **API errors** (backend 500, 400, etc.)
3. **Audio loading errors**
4. **Session errors** (rare, mostly handled by recreating session)

### Error Display Strategy

**Network/API Errors:**
```
Something went wrong while getting that explanation.

[Try again]
```

- Display in conversation thread
- Provide retry button
- Preserve existing messages
- Do NOT show stack traces
- Do NOT render fake assistant response

**Audio Errors:**
```
Couldn't load audio for this episode.
```

- Display in AudioPlayer component
- Allow closing error
- Don't block conversation

**Unsupported Queries (NOT errors):**
- These are successful responses from backend
- Render as normal assistant message
- Do NOT show error UI

---

## Testing Strategy

### Manual Testing Checklist

Per directive section 32, test these scenarios:

**Conversation:**
1. Ask factual question → verify grounded answer
2. Ask conceptual explanation → verify explanation quality
3. Ask follow-up → verify context maintained
4. Ask "explain more simply" → verify adaptation
5. Multi-turn context → verify coherence

**Sources:**
6. Source cards appear with correct structure
7. Episode name matches backend data
8. Timestamp correct and formatted as MM:SS
9. Excerpt displays if provided
10. Audio loads and plays
11. Audio seeks to correct timestamp

**Discovery:**
12. Ask "which material covers X?" → verify conversational response
13. Relevant episodes mentioned naturally in text
14. NO episode browser/selector required

**Comparison:**
15. Ask comparison question → verify multi-episode response
16. Per-episode sources remain distinguishable

**Unsupported:**
17. Ask unsupported question → verify graceful refusal
18. Displayed as trustworthy response, not error

**Errors:**
19. Simulate backend error → verify error message + retry
20. Simulate audio error → verify audio error handling

### Test Environment Setup

**Backend:**
```bash
cd /path/to/fermi-companion
python -m src.api
```

**Frontend:**
```bash
cd frontend
npm run dev
```

**Test Cases:** Use evaluation cases from `eval/results/eval_improved_full_*.json` as test queries

---

## Responsive Design

### Breakpoints

```css
/* Mobile first */
sm: 640px   /* Small tablets */
md: 768px   /* Tablets */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
```

### Layout Adaptations

**Desktop (≥1024px):**
- Single column conversation (max-width: 800px, centered)
- Audio player: full-width bottom bar
- Composer: fixed at bottom of conversation area
- Generous whitespace

**Tablet (768px - 1023px):**
- Conversation width: 90%
- Reduced padding
- Audio player: same as desktop
- Touch-friendly tap targets (min 44x44px)

**Mobile (<768px):**
- Conversation width: 100% (small horizontal padding)
- Header collapses to single line
- Audio player: compact bottom bar
- Composer: bottom sheet style
- Source cards: stack vertically
- Reduced text sizes (still readable)

### No Horizontal Overflow

- All containers: `overflow-x: hidden` or proper max-width
- Long URLs: `word-break: break-all`
- Code blocks: `overflow-x: auto` with scroll
- Images: `max-width: 100%`

---

## Visual Design System

### Typography

**Primary Font:** System UI font stack
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
```

**Scale:**
- Display (title): 2rem (32px) - font-bold
- Heading: 1.5rem (24px) - font-semibold
- Body: 1rem (16px) - font-normal
- Small: 0.875rem (14px) - font-normal
- Caption: 0.75rem (12px) - font-medium

**Line Height:**
- Headings: 1.2
- Body: 1.6
- Code: 1.5

### Color Palette

**Neutral Scale:**
```
50:  #fafafa (backgrounds)
100: #f5f5f5 (subtle backgrounds)
200: #e5e5e5 (borders)
300: #d4d4d4
400: #a3a3a3 (muted text)
500: #737373
600: #525252 (secondary text)
700: #404040 (body text)
800: #262626
900: #171717 (headings)
```

**Accent (Blue - scientific, trustworthy):**
```
500: #3b82f6 (primary actions)
600: #2563eb (hover states)
700: #1d4ed8 (active states)
```

**Semantic:**
- Error: #ef4444 (red-500)
- Success: #10b981 (green-500)
- Warning: #f59e0b (amber-500)

### Spacing System

Tailwind default scale (4px base):
- 1: 4px
- 2: 8px
- 3: 12px
- 4: 16px
- 6: 24px
- 8: 32px
- 12: 48px
- 16: 64px

### Component Styles

**SourceCard:**
- Background: neutral-50
- Border: 1px solid neutral-200
- Border-radius: 8px
- Padding: 16px
- Shadow: subtle (0 1px 3px rgba(0,0,0,0.1))

**UserMessage:**
- Background: neutral-100
- Padding: 12px 16px
- Border-radius: 12px
- Align: right
- Max-width: 80%

**AssistantMessage:**
- Background: transparent
- Padding: 12px 0
- Align: left
- Max-width: 100%

**Composer:**
- Border: 2px solid neutral-200 (focus: blue-500)
- Border-radius: 12px
- Padding: 12px 16px
- Background: white
- Shadow on focus: 0 0 0 3px rgba(59,130,246,0.1)

**Button (Primary):**
- Background: blue-500
- Color: white
- Padding: 8px 16px
- Border-radius: 8px
- Hover: blue-600
- Active: blue-700
- Focus: ring-2 ring-blue-300

---

## Accessibility

### Keyboard Navigation

**Required interactions:**
- Tab through all interactive elements
- Enter to submit message
- Space to play/pause audio
- Arrow keys for audio seek (browser default)
- Escape to clear error messages

**Focus indicators:**
- Visible outline (2px solid blue-500)
- Outline offset: 2px
- Never `outline: none` without custom focus style

### Screen Reader Support

**Semantic HTML:**
```html
<main aria-label="Conversation">
  <div role="log" aria-live="polite" aria-relevant="additions">
    <!-- Message list -->
  </div>
</main>

<form aria-label="Ask a question">
  <textarea aria-label="Your question" />
  <button aria-label="Send message">Send</button>
</form>

<audio aria-label="Episode audio player" />
```

**Dynamic content:**
- New messages: `aria-live="polite"` on message container
- Loading states: `aria-busy="true"`
- Error messages: `role="alert"`

### Color Contrast

**Minimum ratios:**
- Body text (neutral-700 on white): 7:1 ✓
- Small text (neutral-600 on white): 4.5:1 ✓
- Interactive elements: 3:1 ✓
- Disabled text: May fall below (acceptable per WCAG)

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Performance Considerations

### Optimization Strategy

**Do NOT prematurely optimize.** Implement cleanly first, then profile.

**Potential optimizations (only if needed):**

1. **Message List Virtualization**
   - Only if >100 messages in conversation
   - Use react-window or similar
   - Most conversations won't need this

2. **Debounce Audio Seek**
   - Prevent excessive seek operations during slider drag
   - 100ms debounce sufficient

3. **Lazy Load Audio**
   - Audio loads on-demand (already happening)
   - Don't preload all episodes

4. **Markdown Memoization**
   - Memoize react-markdown rendering if re-renders are frequent
   - Use React.memo() on AssistantMessage

5. **Image Optimization**
   - If images added later, use proper formats (WebP, AVIF)
   - Lazy loading for images below fold

### Bundle Size Targets

- Initial JS: <200KB gzipped
- React + ReactDOM: ~45KB
- react-markdown: ~30KB
- Tailwind (purged): ~10KB
- App code: <100KB

**Monitor with:** `npm run build` → check dist/ size

---

## Development Workflow

### Setup Commands

```bash
# Initialize project
npm create vite@latest frontend -- --template react-ts
cd frontend

# Install dependencies
npm install
npm install -D tailwindcss postcss autoprefixer
npm install react-markdown

# Initialize Tailwind
npx tailwindcss init -p

# Start dev server
npm run dev
```

### Environment Variables

Create `.env`:
```
VITE_API_BASE_URL=http://localhost:8000
```

### Development Commands

```bash
npm run dev        # Start dev server (http://localhost:5173)
npm run build      # Production build
npm run preview    # Preview production build
npm run lint       # ESLint
```

### Backend Integration During Development

**Option 1: Vite Proxy** (Preferred)
```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/chat': 'http://localhost:8000',
      '/episodes': 'http://localhost:8000',
    }
  }
})
```

**Option 2: CORS Middleware**
Add CORS to FastAPI (see API Contract section)

---

## Implementation Phases

### Phase 1: Backend Contract (3-4 hours)

**Tasks:**
1. Add `SourceEvidence` model to `src/api.py`
2. Modify `ChatResponse` to include `sources: List[SourceEvidence]`
3. Update `/chat` endpoint to map `state.last_retrieved_evidence` to SourceEvidence objects
4. Add `GET /episodes/{episode_id}/audio` endpoint with validation
5. Add CORS middleware if needed
6. Test with curl/httpx:
   ```bash
   # Test structured sources
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"session_id":"test","message":"Explain special relativity"}'
   
   # Test audio endpoint
   curl -I http://localhost:8000/episodes/ep01/audio
   ```

**Verification:** JSON response contains `sources` array with episode_id, timestamps

### Phase 2: Frontend Shell (2-3 hours)

**Tasks:**
1. Initialize Vite + React + TypeScript project
2. Install dependencies (Tailwind, react-markdown)
3. Configure Tailwind
4. Create basic Layout component
5. Create Header with "Fermi Companion" title
6. Create ConversationView shell
7. Create EmptyState component
8. Set up routing (if needed - likely single route)
9. Configure Vite proxy for backend
10. Test: Render empty state, verify styling

**Verification:** App loads, shows empty state, responsive

### Phase 3: Core Conversation (4-5 hours)

**Tasks:**
1. Create API client (`src/api/client.ts`)
2. Implement ConversationContext with state management
3. Create Composer component with textarea + submit
4. Implement useSession hook for session ID generation
5. Create MessageList component
6. Create UserMessage component
7. Create AssistantMessage component with react-markdown
8. Connect Composer to ConversationContext.sendMessage
9. Handle loading states
10. Handle error states with retry
11. Test: Send real message, receive real response

**Verification:** Can ask question, receive response, see conversation history

### Phase 4: Source Verification (3-4 hours)

**Tasks:**
1. Create SourceCard component
2. Implement timestamp formatting utility (seconds → MM:SS)
3. Render sources in AssistantMessage
4. Create AudioContext
5. Create AudioPlayer component
6. Implement playFromTimestamp functionality
7. Connect SourceCard "Listen from..." button to AudioContext
8. Handle audio loading states
9. Handle audio errors
10. Test: Click source, audio loads and seeks to timestamp

**Verification:** Source cards appear, audio plays from correct timestamp

### Phase 5: Follow-up Learning (1-2 hours)

**Tasks:**
1. Verify conversation context maintained across turns
2. Test follow-up questions
3. Test "explain more simply" pattern
4. Optionally add contextual suggestion buttons (if time permits)

**Verification:** Multi-turn conversations work, context preserved

### Phase 6: Conversational Discovery (1 hour)

**Tasks:**
1. Test discovery queries through normal conversation
2. Verify responses render naturally (no special UI needed)
3. Test: "Which material covers information theory?"
4. Test: "What should I explore for biology?"

**Verification:** Discovery works conversationally, no episode browser UI

### Phase 7: Comparison (1 hour)

**Tasks:**
1. Test comparison queries
2. Verify multi-source rendering
3. Ensure per-episode provenance clear in UI
4. Test: "Compare Einstein and Bell"

**Verification:** Comparison responses show sources from different episodes

### Phase 8: Unsupported Behavior (30 min)

**Tasks:**
1. Test unsupported queries
2. Verify unsupported response renders as normal message (not error)
3. Test: "Explain string theory"
4. Test: "Who won the World Series?"

**Verification:** Unsupported responses feel intentional, not like failures

### Phase 9: Polish (3-4 hours)

**Tasks:**
1. Refine typography (font sizes, weights, line heights)
2. Adjust spacing throughout
3. Improve source card visual hierarchy
4. Add subtle transitions (opacity, transform)
5. Polish empty state copy
6. Improve loading indicators
7. Improve error message clarity
8. Responsive testing and fixes
9. Accessibility audit (keyboard nav, focus states, ARIA labels)
10. Cross-browser testing (Chrome, Firefox, Safari)
11. Mobile testing

**Verification:** UI feels calm, scientific, editorial, trustworthy

---

## Risks and Mitigations

### Risk 1: Audio File Size / Bandwidth
**Impact:** Episodes 30-50MB each, slow loading  
**Mitigation:** HTTP range requests allow progressive loading (browser native)  
**Acceptance:** User only loads audio when clicking "Listen"

### Risk 2: Session Loss on Backend Restart
**Impact:** In-memory sessions lost if backend crashes  
**Mitigation:** Frontend stores session ID but can't guarantee persistence  
**Acceptance:** Documented limitation, user can start new conversation

### Risk 3: Markdown Citation Parsing During Transition
**Impact:** If structured sources added incrementally, may need both  
**Mitigation:** Add structured sources first, keep markdown for fallback  
**Acceptance:** Brief transition period acceptable

### Risk 4: CORS Issues
**Impact:** Frontend blocked by CORS during development  
**Mitigation:** Add CORS middleware or use Vite proxy  
**Acceptance:** Standard development pattern

### Risk 5: Long Assistant Responses
**Impact:** Very long responses may cause scroll/render issues  
**Mitigation:** CSS max-height with scroll, or lazy rendering  
**Acceptance:** Unlikely with current backend behavior

---

## Success Criteria

### Must Have (P0)
✅ Learner can ask questions and receive grounded answers  
✅ Sources displayed with episode, timestamp, excerpt  
✅ Audio playback from specific timestamps works  
✅ Conversation-first UI (no episode browser)  
✅ Mobile responsive  
✅ Unsupported queries handled gracefully  
✅ Loading and error states clear  

### Should Have (P1)
✅ Comparison responses show multi-episode sources  
✅ Follow-up context maintained  
✅ Keyboard accessible  
✅ Readable contrast  

### Nice to Have (P2)
⚠️ Contextual follow-up suggestion buttons (if time)  
⚠️ Smooth animations (if time)  
⚠️ Markdown syntax highlighting (if time)  

---

## Maintenance and Future Considerations

### Not in Scope for Initial Implementation

- Conversation persistence across sessions
- Conversation history browser
- Export conversation
- Share conversation
- Multiple concurrent conversations
- User authentication
- Episode bookmarking
- Highlighting in excerpts
- Advanced audio features (speed, skip)

### Potential Future Enhancements

If the product evolves beyond trial scope:

1. **Conversation Persistence:**
   - Backend session storage (Redis, PostgreSQL)
   - Conversation list UI
   - Resume previous conversations

2. **Enhanced Source Verification:**
   - Highlight relevant portion of excerpt
   - Show multiple sources inline with answer text
   - Source timestamp heat map

3. **Collaboration:**
   - Share conversation link
   - Multi-user learning sessions

4. **Advanced Discovery:**
   - Conversational recommendation refinement
   - Learning pathways

**Important:** None of these should introduce episode browsing as primary navigation.

---

## Conclusion

This design implements a **conversation-first learning companion** that helps learners understand scientific ideas through natural dialogue, grounded in source audio.

**Key Architectural Decisions:**

1. **No episode browser** - Discovery is conversational
2. **Minimal backend changes** - Reuse existing evidence structures
3. **Simple state management** - React Context, no Redux
4. **Compact audio player** - Source verification, not podcast app
5. **Clean, editorial design** - Scientific, trustworthy, calm

**Next Step:** Proceed to implementation (tasks.md) following the phased approach defined above.

