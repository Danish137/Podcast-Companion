# Fermi Companion — Cross-IDE Frontend Technical Assessment

**Assessment Date:** 2026-08-16  
**IDE:** Kiro  
**Phase:** Pre-implementation Analysis  
**Assessor:** Frontend Integration Agent

---

## Executive Summary

This document provides a comprehensive technical assessment of the Fermi Companion project state prior to frontend implementation. The backend system is **fully functional** with all 16 episodes ingested, a working RAG pipeline, conversation management, and a successfully evaluated improvement. The frontend **does not yet exist**. This assessment identifies the minimal backend changes required and recommends a pragmatic frontend architecture that reuses existing evidence structures.

**Key Findings:**
- ✅ Backend is production-ready with proven evaluation results (10/10 cases passing)
- ✅ Evidence structures (chunks, metadata, sources) are well-designed and reusable
- ⚠️ API contract needs structured sources endpoint to avoid fragile markdown parsing
- ⚠️ No audio serving mechanism exists yet
- ⚠️ No episode catalogue API endpoint exists yet
- ✅ Session management architecture is sound (in-memory, explicit session_id)

---

## 1. Actual Project State

### 1.1 Repository Structure

```
fermi-companion/
├── .env                          # API keys (OPENROUTER_API_KEY configured)
├── requirements.txt              # Python dependencies
├── Podcast/                      # 16 raw MP3 files (~9.6 hours)
├── data/
│   ├── transcripts/              # 16 timestamped transcript JSON files
│   ├── chunks/                   # 16 chunk files with provenance
│   ├── metadata/                 # 16 episode metadata + manifest.json
│   └── index/chroma_db/          # ChromaDB vector store (passages + episodes)
├── src/
│   ├── transcribe.py             # Audio → timestamped transcripts
│   ├── chunker.py                # Transcripts → retrieval chunks
│   ├── metadata.py               # Transcript → episode metadata
│   ├── retrieval.py              # ChromaDB wrapper (passage/episode query)
│   ├── companion.py              # Core conversation logic + intent routing
│   ├── api.py                    # FastAPI backend (2 endpoints)
│   ├── cli.py                    # Terminal interface for testing
│   ├── config.py                 # Environment config
│   └── evaluate.py               # Evaluation framework
├── eval/results/                 # 3 evaluation runs (baseline + improved)
└── [PROJECT DOCS]                # AGENTS.md, STATUS.md, DECISIONS.md, etc.
```

### 1.2 Corpus

**Verified:** 16 episodes from "Great Papers" series
- **Total Duration:** 578.8 minutes (9.6 hours)
- **Fields:** Physics (9), Biology (3), CS (2), Math (1), Information Theory (1)
- **Date Range:** 1858-2017
- **All audio ingested:** Transcripts, chunks, metadata, and ChromaDB index complete

**Discrepancy Note:** Assignment brief specified 3 files / ≤3 hours. Actual corpus is 16 files / 9.6 hours. Documented in DECISIONS.md D003. System supports arbitrary episode count.

### 1.3 Technology Stack

**Backend (Verified Installed):**
- Python 3.14.0
- FastAPI 0.135.3
- OpenRouter API (Gemini 2.5 Flash for transcription & chat)
- ChromaDB (for vector retrieval)
- httpx, pydantic, rich, uvicorn

**Audio:**
- ffmpeg 8.1.2-essentials (for audio segment splitting)
- Raw MP3 format

**Frontend (None):**
- No frontend code exists yet
- No package.json or node_modules

---

## 2. Backend Architecture

### 2.1 Data Flow

```
User Query
    ↓
FastAPI POST /chat {session_id, message}
    ↓
FermiCompanion.route_intent() → EXPLAIN | COMPARE | DISCOVER | UNSUPPORTED
    ↓
Intent-specific retrieval:
    EXPLAIN    → query_passages() → ChromaDB passages collection
    COMPARE    → query_episodes() + query_passages_multi_episode()
    DISCOVER   → inject full episode_manifest.json (bypass retrieval)
    UNSUPPORTED→ no retrieval
    ↓
Evidence formatting → string concatenation
    ↓
LLM call with GENERATION_PROMPT or DISCOVERY_PROMPT
    ↓
Response with embedded markdown citations: [Episode Title, MM:SS]
    ↓
ChatResponse {response: str, intent_used: str}
    ↓
Frontend (does not exist)
```

### 2.2 Evidence Structures

**Chunk Object** (from `data/chunks/*.json`):
```json
{
  "chunk_id": "ep01_chunk_000",
  "episode_id": "ep01",
  "episode_title": "Einstein's Special Relativity",
  "start_time": 0.0,
  "end_time": 90.0,
  "text": "...",
  "word_count": 187,
  "duration_seconds": 90.0
}
```

**Episode Metadata** (from `data/metadata/episode_manifest.json`):
```json
{
  "episode_id": "ep01",
  "episode_title": "Einstein's Special Relativity",
  "filename": "Great Papers 01 - Einstein_s Special Relativity.mp3",
  "duration_seconds": 3134.011438,
  "paper_title": "On the Electrodynamics of Moving Bodies",
  "authors": ["Einstein"],
  "publication_year": 1905,
  "field": "Physics",
  "subfield": "Special Relativity",
  "key_concepts": ["Electrodynamics", "Maxwell's equations", ...],
  "summary": "...",
  "disciplines": ["Physics"]
}
```

**Retrieval Result** (from `query_passages()`):
```python
{
  "chunk_id": "ep01_chunk_003",
  "text": "...",
  "episode_id": "ep01",
  "episode_title": "Einstein's Special Relativity",
  "start_time": 270.0,
  "end_time": 360.0,
  "score": 0.85  # cosine similarity
}
```

**Key Observation:** The retrieval layer already produces rich evidence objects with all necessary provenance. These should be exposed directly to the frontend rather than creating new representations.

### 2.3 Current API Endpoints

#### `POST /chat`

**Request:**
```json
{
  "session_id": "string",
  "message": "string"
}
```

**Response:**
```json
{
  "response": "string",  // Markdown with embedded citations like [Episode, MM:SS]
  "intent_used": "string"  // EXPLAIN | COMPARE | DISCOVER | UNSUPPORTED
}
```

#### `GET /health`

**Response:**
```json
{
  "status": "ok"
}
```

**Critical Gap:** Sources are embedded in markdown text. The frontend would need regex parsing to extract episode/timestamp, creating a fragile contract.

---

## 3. Current Source/Provenance Representation

### 3.1 How Sources Currently Work

**Example response from eval C02:**
```
"According to Hawking, black holes radiate due to the interplay of general 
relativity and quantum field theory at the event horizon [How Black Holes 
Radiate, Hawking 1975, 44:00]. This radiation, known as Hawking radiation..."
```

**Format:** `[Episode Title, MM:SS]`

**Problems for Frontend:**
1. No structured episode ID (only human title)
2. Timestamps are formatted strings, not seconds
3. No excerpt boundaries provided
4. No way to distinguish citation from other markdown brackets
5. Requires brittle regex parsing in client
6. No audio file mapping

### 3.2 Evidence Already Available in Backend

During processing, `companion.py`:
1. Retrieves rich passage objects with full provenance
2. Stores them in `state.last_retrieved_evidence`
3. Formats them as text strings for LLM context
4. LLM generates citations in markdown
5. **Discards the structured evidence objects**

The evidence objects are **already available** but not exposed in the API response.

---

## 4. Current Audio Representation

### 4.1 Audio File Structure

Located in `Podcast/`:
```
Great Papers 01 - Einstein_s Special Relativity.mp3
Great Papers 02 - How Black Holes Radiate, Hawking 1975.mp3
...
Great Papers 16 - Nash Equilibrium and Game Theory, 1950.mp3
```

### 4.2 Filename → Episode ID Mapping

Handled in `transcribe.py`:
```python
def parse_episode_id(filename: str) -> str:
    match = re.match(r'Great Papers (\d+)', filename)
    if match:
        return f"ep{int(match.group(1)):02d}"
```

**Canonical mapping exists** in `episode_manifest.json` via the `filename` field.

### 4.3 Current Audio Access

**Status:** No HTTP endpoint exists to serve audio files.

**Risk:** Directly exposing `Podcast/` directory would allow arbitrary file access.

**Required:** Controlled audio endpoint that validates episode ID and serves only known audio files.

---

## 5. Current Manifest/Catalogue Representation

### 5.1 Episode Manifest Location

`data/metadata/episode_manifest.json` contains complete metadata for all 16 episodes.

Generated by `metadata.py` from transcripts using Gemini extraction.

### 5.2 Discovery Implementation

**Current Behavior (DISCOVER intent):**
```python
# companion.py line ~120
if intent == "DISCOVER":
    manifest_path = METADATA_DIR / "episode_manifest.json"
    with open(manifest_path, encoding="utf-8") as f:
        episodes = json.load(f)
    evidence_text = self.format_episode_evidence(episodes)
    prompt = DISCOVERY_PROMPT.format(evidence=evidence_text, question=question)
```

**The full manifest is injected into LLM context** (bypassing semantic retrieval per DECISIONS.md D008).

### 5.3 Catalogue API Status

**Status:** No `/episodes` endpoint exists.

**Risk:** Frontend would need to hardcode episode data or duplicate the manifest file.

**Required:** Expose manifest through API endpoint.

---

## 6. Current Conversation/Session Architecture

### 6.1 Session State

```python
# api.py line ~12
sessions: Dict[str, ConversationState] = {}
```

**Storage:** In-memory dictionary keyed by `session_id`

**ConversationState:**
```python
@dataclass
class ConversationState:
    history: List[Dict[str, str]] = field(default_factory=list)
    last_retrieved_evidence: List[dict] = field(default_factory=list)
    current_episode_focus: Optional[str] = None
```

### 6.2 Session Lifecycle

1. Frontend sends `session_id` in `/chat` request
2. Backend creates new `ConversationState` if session doesn't exist
3. State persists for application lifetime
4. **State lost on backend restart**

### 6.3 Conversation Context

- Last 4 history messages sent to intent router for context
- Previous retrieved evidence reused for follow-ups (if question is <8 words)
- Episode focus tracked for scoped retrieval

**Architecture is sound.** No changes needed. Frontend should generate UUID session IDs and store them in browser.

---

## 7. Verification Against Handoff Document Claims

### Claim 1: "There is no frontend"
✅ **VERIFIED TRUE** — No HTML, CSS, JS, React, or frontend files exist

### Claim 2: "/chat only returns markdown response + intent"
✅ **VERIFIED TRUE** — Response schema: `{response: str, intent_used: str}`

### Claim 3: "Sources are embedded in markdown"
✅ **VERIFIED TRUE** — Citations formatted as `[Episode Title, MM:SS]`

### Claim 4: "Audio is not currently exposed through HTTP"
✅ **VERIFIED TRUE** — No audio serving endpoint exists

### Claim 5: "Episode manifest not exposed as API"
✅ **VERIFIED TRUE** — No `/episodes` endpoint exists

### Claim 6: "Session state is in-memory"
✅ **VERIFIED TRUE** — `sessions: Dict[str, ConversationState] = {}`

### Claim 7: "Discovery handled through existing backend intent"
✅ **VERIFIED TRUE** — DISCOVER intent bypasses ChromaDB, injects manifest

### Claim 8: "Comparison handled through existing backend intent"
✅ **VERIFIED TRUE** — COMPARE intent uses `query_passages_multi_episode()`

### Claim 9: "Unsupported behavior already implemented"
✅ **VERIFIED TRUE** — UNSUPPORTED intent returns refusal message

**All claims verified.** The handoff document accurately describes the current state.

---

## 8. Frontend Integration Gaps

### Gap 1: Structured Source Metadata

**Current:** Markdown citations `[Episode, MM:SS]`  
**Problem:** Requires regex parsing, no episode ID, no audio link  
**Required:** Extend `ChatResponse` with structured sources

**Proposed Addition:**
```python
class SourceEvidence(BaseModel):
    episode_id: str
    episode_title: str
    start_time: float
    end_time: float
    timestamp_formatted: str  # "MM:SS"
    text_excerpt: Optional[str]
    score: Optional[float]

class ChatResponse(BaseModel):
    response: str
    intent_used: str
    sources: List[SourceEvidence] = []
```

**Implementation:** Return `state.last_retrieved_evidence` formatted as `SourceEvidence` objects

### Gap 2: Episode Catalogue API

**Current:** Manifest only accessible via filesystem  
**Problem:** Frontend would duplicate or hardcode data  
**Required:** New endpoint

**Proposed Addition:**
```python
@app.get("/episodes")
async def get_episodes():
    manifest_path = METADATA_DIR / "episode_manifest.json"
    with open(manifest_path) as f:
        episodes = json.load(f)
    return {"episodes": episodes}
```

### Gap 3: Audio Access

**Current:** No HTTP endpoint for audio  
**Problem:** Frontend cannot enable source verification  
**Required:** New endpoint with validation

**Proposed Addition:**
```python
@app.get("/episodes/{episode_id}/audio")
async def get_episode_audio(episode_id: str):
    # Validate episode_id exists in manifest
    # Map episode_id → filename
    # Return FileResponse with audio content
```

### Gap 4: CORS Configuration

**Current:** No CORS headers configured  
**Problem:** Browser will block frontend requests if served from different origin  
**Required:** Add CORS middleware (if frontend served separately)

**Proposed Addition:**
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)
```

### Gap 5: Static Frontend Serving (Optional)

**Current:** FastAPI only serves API  
**Consideration:** Could serve frontend from same process  
**Alternative:** Separate frontend dev server during development

**Decision:** Start with separate dev server. Can consolidate later if needed.

---

## 9. Which Backend Changes Are Genuinely Required

### ✅ REQUIRED: Structured Sources in ChatResponse

**Why:** Avoids fragile regex parsing, provides episode IDs and audio references

**Complexity:** Low — evidence objects already exist in `state.last_retrieved_evidence`

**Risk:** Low — additive change, doesn't break existing markdown citations

### ✅ REQUIRED: GET /episodes

**Why:** Prevents frontend from hardcoding or duplicating manifest

**Complexity:** Trivial — read and return existing JSON file

**Risk:** Minimal — read-only endpoint

### ✅ REQUIRED: GET /episodes/{episode_id}/audio

**Why:** Enables core product feature (source verification)

**Complexity:** Medium — needs validation, file mapping, range support

**Risk:** Medium — must prevent arbitrary file access

### ⚠️ CONDITIONAL: CORS Middleware

**Why:** Required if frontend runs on different port/domain during development

**Complexity:** Trivial — one middleware line

**Risk:** Minimal — development-only concern

**Decision:** Add only if cross-origin issues occur

### ❌ NOT REQUIRED: Separate Session Persistence

**Current in-memory architecture is acceptable** for trial scope. Frontend should handle session ID generation/storage.

### ❌ NOT REQUIRED: Streaming Responses

No evidence of backend supporting streaming. Frontend should use standard request/response.

### ❌ NOT REQUIRED: Authentication

Not in product scope per AGENTS.md

---

## 10. Better Alternatives Using Existing Mechanisms

### Alternative 1: Reuse Existing Evidence Objects

**Proposed approach:** Return `state.last_retrieved_evidence` directly  
**Better approach:** ✅ Same — these objects already have correct structure

**No improvement needed.** Direct reuse is optimal.

### Alternative 2: Episode Metadata Service Layer

**Proposed approach:** Create new metadata service  
**Better approach:** ❌ **Use existing manifest directly**

The manifest is already canonical. No service layer needed.

### Alternative 3: Complex Audio Streaming

**Proposed approach:** Implement HLS/DASH streaming  
**Better approach:** ❌ **Use HTTP range requests**

HTTP range requests (standard browser behavior) are sufficient for seekable audio.

### Alternative 4: GraphQL API

**Proposed approach:** Migrate to GraphQL  
**Better approach:** ❌ **Keep REST**

Current API is simple and sufficient. GraphQL adds complexity without value.

### Alternative 5: Separate Retrieval Endpoint for Frontend

**Proposed approach:** Add `/search` endpoint for direct frontend retrieval  
**Better approach:** ❌ **Keep single /chat endpoint**

Per handoff doc: "Never perform a second frontend retrieval." Sources must come from same evidence path that generated the answer.

---

## 11. Recommended Frontend Architecture

### 11.1 Technology Stack

**Framework:** React 18+ with TypeScript  
**Rationale:** Industry standard, excellent TypeScript support, large ecosystem

**Build Tool:** Vite  
**Rationale:** Fast development server, optimal for this project size

**Styling:** Tailwind CSS  
**Rationale:** Rapid development, utility-first, avoids custom CSS

**State Management:** React Context + useState  
**Rationale:** Application is simple enough not to need Redux/Zustand

**HTTP Client:** fetch (native) + thin wrapper  
**Rationale:** No need for axios overhead

### 11.2 Project Structure

```
frontend/
├── public/
├── src/
│   ├── api/
│   │   └── client.ts           # API layer
│   ├── components/
│   │   ├── Conversation/
│   │   │   ├── MessageList.tsx
│   │   │   ├── UserMessage.tsx
│   │   │   ├── AssistantMessage.tsx
│   │   │   ├── SourceCard.tsx
│   │   │   └── Composer.tsx
│   │   ├── Explore/
│   │   │   ├── EpisodeList.tsx
│   │   │   └── EpisodeCard.tsx
│   │   ├── AudioPlayer.tsx
│   │   └── Layout.tsx
│   ├── hooks/
│   │   ├── useChat.ts
│   │   ├── useSession.ts
│   │   └── useEpisodes.ts
│   ├── types/
│   │   └── api.ts              # TypeScript interfaces for API
│   ├── App.tsx
│   └── main.tsx
├── package.json
└── vite.config.ts
```

### 11.3 Component Hierarchy

```
App
├── Layout
│   ├── ConversationView
│   │   ├── EmptyState (when no messages)
│   │   ├── MessageList
│   │   │   ├── UserMessage
│   │   │   └── AssistantMessage
│   │   │       ├── ResponseText (markdown)
│   │   │       └── SourceCard[]
│   │   └── Composer
│   │       ├── Input
│   │       ├── SendButton
│   │       └── LoadingIndicator
│   └── Sidebar
│       ├── NewConversationButton
│       └── EpisodeList (Explore)
│           └── EpisodeCard[]
└── AudioPlayer (global)
```

### 11.4 State Architecture

**Conversation State:**
```typescript
{
  sessionId: string;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}
```

**Episode State:**
```typescript
{
  episodes: Episode[];
  isLoading: boolean;
  selectedEpisode: Episode | null;
}
```

**Audio State:**
```typescript
{
  currentEpisode: string | null;
  currentTime: number;
  isPlaying: boolean;
}
```

**State Management:** React Context for global state, useState for component-local state

### 11.5 No Over-Engineering

**What NOT to add:**
- Redux/MobX (overkill for this size)
- Complex animation libraries (GSAP, Framer Motion beyond basics)
- Virtual scrolling (conversation likely < 100 messages)
- Service workers / PWA features
- Complex routing (single conversation view)
- Backend state synchronization (optimistic updates not needed)

---

## 12. Recommended Component Design

### 12.1 Conversation Components

**MessageList:**
- Scroll to bottom on new messages
- Render user/assistant messages
- Simple reverse chronological layout

**AssistantMessage:**
- Markdown rendering (react-markdown)
- Embedded SourceCard components
- Intent-aware styling (comparison vs explanation)

**SourceCard:**
- Episode badge (title, field)
- Timestamp range (MM:SS - MM:SS)
- Excerpt text (if available)
- "Listen from MM:SS" button
- Click to play audio

**Composer:**
- Textarea with auto-resize
- Submit on Enter (Shift+Enter for newline)
- Disabled during loading
- Character count (optional)

### 12.2 Explore Components

**EpisodeList:**
- Grid/list of EpisodeCard
- Search/filter by field, keyword, year
- Click to view full metadata

**EpisodeCard:**
- Episode title
- Paper title (year)
- Field badge
- Key concepts (first 5)
- Click to expand or start conversation

### 12.3 AudioPlayer Component

**Features:**
- Compact bar at bottom of viewport
- Episode title
- Play/pause, seek bar
- Current time / duration
- Jump to timestamp from SourceCard

**Implementation:**
- HTML5 `<audio>` element
- Controlled via ref
- Seekable via HTTP range requests

---

## 13. Recommended API Contract

### 13.1 Modified POST /chat Response

```typescript
interface ChatResponse {
  response: string;           // Markdown (keep for backward compat)
  intent_used: string;        // EXPLAIN | COMPARE | DISCOVER | UNSUPPORTED
  sources: SourceEvidence[];  // NEW
}

interface SourceEvidence {
  episode_id: string;         // "ep01"
  episode_title: string;      // "Einstein's Special Relativity"
  start_time: number;         // 270.0 (seconds)
  end_time: number;           // 360.0
  timestamp_formatted: string;// "04:30 - 06:00"
  text_excerpt?: string;      // First 200 chars of chunk
  score?: number;             // 0.85 (relevance)
}
```

### 13.2 New GET /episodes

```typescript
interface EpisodesResponse {
  episodes: Episode[];
}

interface Episode {
  episode_id: string;
  episode_title: string;
  filename: string;
  duration_seconds: number;
  paper_title: string;
  authors: string[];
  publication_year: number;
  field: string;
  subfield: string;
  key_concepts: string[];
  summary: string;
  disciplines: string[];
}
```

### 13.3 New GET /episodes/{episode_id}/audio

**Request:**
```
GET /episodes/ep01/audio
Range: bytes=0-
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

**Validation:**
- Return 404 if episode_id not in manifest
- Return 400 if episode_id format invalid
- Support HTTP range requests for seeking

---

## 14. Risks and Mitigations

### Risk 1: Audio File Size / Bandwidth

**Risk:** Episodes are 30-50 MB each. Slow loading.  
**Mitigation:** HTTP range requests allow progressive loading. Browser handles this natively.  
**Acceptable:** User only loads audio when clicking "Listen"

### Risk 2: Session Loss on Backend Restart

**Risk:** In-memory sessions lost if backend crashes  
**Mitigation:** Frontend stores session ID but doesn't guarantee persistence  
**Acceptable:** Trial scope limitation. Document in UI.

### Risk 3: Markdown Citation Parsing During Transition

**Risk:** If structured sources added incrementally, frontend might need to support both  
**Mitigation:** Add structured sources first, keep markdown for fallback  
**Acceptable:** Brief transition period

### Risk 4: ChromaDB Index Rebuilding

**Risk:** If ChromaDB index corrupted, retrieval fails  
**Mitigation:** `retrieval.py build` command exists for rebuild  
**Acceptable:** Documented recovery procedure

### Risk 5: CORS Issues During Development

**Risk:** Frontend dev server (localhost:5173) blocked by backend (localhost:8000)  
**Mitigation:** Add CORS middleware early in dev  
**Acceptable:** Standard development pattern

---

## 15. What Should Be Implemented First

### Phase 1: Backend Contract Changes (2-3 hours)

**Priority 1.1:** Extend ChatResponse with structured sources
- Add `SourceEvidence` model to `api.py`
- Modify `/chat` endpoint to return `state.last_retrieved_evidence`
- Format timestamp strings (MM:SS)
- Test with curl/httpx

**Priority 1.2:** Add GET /episodes endpoint
- Read episode_manifest.json
- Return as JSON
- Test with curl

**Priority 1.3:** Add GET /episodes/{episode_id}/audio endpoint
- Validate episode_id against manifest
- Map to filename
- Return FileResponse with audio
- Support HTTP range requests
- Test with curl + browser

**Priority 1.4:** Add CORS middleware
- Development-only configuration
- Test cross-origin requests

**Deliverable:** Backend API ready for frontend integration

### Phase 2: Frontend Skeleton (2-3 hours)

**Priority 2.1:** Initialize React + Vite project
- `npm create vite@latest frontend -- --template react-ts`
- Install dependencies (tailwindcss, react-markdown)
- Configure Vite proxy to backend

**Priority 2.2:** Create API client layer
- `src/api/client.ts` with typed fetch wrappers
- `chat()`, `getEpisodes()`, `getAudio()`

**Priority 2.3:** Build layout structure
- Layout component (sidebar + main)
- Routing (if needed)
- Responsive breakpoints

**Deliverable:** Running React app that can call backend

### Phase 3: Core Conversation (3-4 hours)

**Priority 3.1:** Build Composer component
- Textarea with submit
- Session ID generation (UUID)
- Store in localStorage

**Priority 3.2:** Build MessageList component
- User/Assistant message display
- Markdown rendering
- Auto-scroll

**Priority 3.3:** Integrate /chat endpoint
- useChat hook with async logic
- Loading states
- Error handling

**Priority 3.4:** Build SourceCard component
- Display structured sources
- Timestamp formatting
- Excerpt display

**Deliverable:** Working conversation with sources

### Phase 4: Audio Integration (2-3 hours)

**Priority 4.1:** Build AudioPlayer component
- HTML5 audio element
- Play/pause controls
- Seek bar

**Priority 4.2:** Integrate with SourceCard
- "Listen from MM:SS" button
- Seek to timestamp on click

**Priority 4.3:** Handle loading/errors
- Loading spinner for audio fetch
- Error message if episode not found

**Deliverable:** Playable audio with timestamp seeking

### Phase 5: Episode Catalogue (2-3 hours)

**Priority 5.1:** Build EpisodeList component
- Fetch from /episodes
- Display grid/list

**Priority 5.2:** Build EpisodeCard component
- Episode metadata display
- Field badges
- Key concepts

**Priority 5.3:** Add search/filter
- Text search across fields
- Filter by discipline, year range

**Deliverable:** Browsable episode catalogue

### Phase 6: Polish & States (2-3 hours)

**Priority 6.1:** Empty state
- Welcome message
- Example queries
- Call-to-action

**Priority 6.2:** Loading states
- Skeleton screens
- Meaningful loading text

**Priority 6.3:** Error states
- Retry buttons
- Friendly error messages

**Priority 6.4:** Responsive design
- Mobile layout
- Touch-friendly controls

**Deliverable:** Complete UX with all states

### Phase 7: Testing & Verification (1-2 hours)

**Priority 7.1:** Manual testing checklist
- All 10 evaluation cases through UI
- Audio playback
- Episode discovery
- Mobile responsive

**Priority 7.2:** Cross-browser testing
- Chrome, Firefox, Safari
- Mobile Safari, Chrome Mobile

**Deliverable:** Verified working frontend

---

## 16. Estimated Implementation Timeline

**Total Estimated Time:** 14-19 hours

**Day 1 (8 hours):**
- Phase 1: Backend contract (3h)
- Phase 2: Frontend skeleton (2h)
- Phase 3: Core conversation (3h)

**Day 2 (8 hours):**
- Phase 3 cont'd: Finish conversation (1h)
- Phase 4: Audio integration (3h)
- Phase 5: Episode catalogue (2h)
- Phase 6: Polish (2h)

**Buffer:** 2-3 hours for unexpected issues

---

## 17. Success Criteria

### Must Have (P0):
✅ Learner can ask questions and receive grounded answers  
✅ Sources displayed with episode, timestamp, excerpt  
✅ Audio playback from specific timestamps works  
✅ Episode catalogue browsable  
✅ Mobile responsive  
✅ Unsupported queries handled gracefully  

### Should Have (P1):
✅ Comparison responses show multi-episode sources  
✅ Follow-up context maintained  
✅ Loading/error states present  
✅ Keyboard accessible  

### Nice to Have (P2):
⚠️ Search/filter episode catalogue (if time)  
⚠️ Follow-up suggestion buttons (if time)  
⚠️ Smooth animations (if time)  

---

## 18. Key Technical Decisions

### Decision 1: React over Vue/Svelte
**Rationale:** Largest ecosystem, best TypeScript support, evaluator likely familiar  
**Trade-off:** Slightly more boilerplate than Svelte  
**Acceptable:** React is industry standard for this type of application

### Decision 2: Tailwind over styled-components
**Rationale:** Faster development, no runtime CSS-in-JS overhead  
**Trade-off:** Utility class verbosity  
**Acceptable:** Prototyping speed prioritized

### Decision 3: Single /chat endpoint over separate endpoints
**Rationale:** Reuses existing proven backend logic, maintains grounding provenance  
**Trade-off:** Frontend cannot do independent retrieval  
**Acceptable:** This is a feature, not a bug (prevents dual truth sources)

### Decision 4: HTTP range requests over streaming
**Rationale:** Simpler implementation, browser-native seeking  
**Trade-off:** Less control over buffering  
**Acceptable:** Sufficient for use case

### Decision 5: localStorage for session ID
**Rationale:** Persists across page reloads, simple API  
**Trade-off:** Session lost if user clears data  
**Acceptable:** User can start new conversation

---

## 19. Known Limitations

1. **Session persistence:** In-memory sessions lost on backend restart
2. **Audio preloading:** Audio loads on-demand, not preloaded
3. **Offline support:** None — requires backend connection
4. **Authentication:** None — open access
5. **Multi-user:** Not supported
6. **Conversation history:** Not persisted beyond browser session
7. **Mobile optimization:** Functional but not heavily optimized
8. **Accessibility:** Basic compliance, not WCAG AAA audited

**All limitations are acceptable** for trial scope per AGENTS.md.

---

## 20. Next Steps

### Immediate Actions:

1. **Review this assessment** with user to confirm approach
2. **Create design spec** with wireframes/mockups
3. **Create tasks.md** with implementation checklist
4. **Begin Phase 1** (backend contract changes)

### Do NOT Proceed Until:

- User explicitly approves requirements
- User explicitly approves design approach
- User explicitly approves task list

---

## Appendices

### Appendix A: Example API Responses

**GET /episodes** (excerpt):
```json
{
  "episodes": [
    {
      "episode_id": "ep01",
      "episode_title": "Einstein's Special Relativity",
      "paper_title": "On the Electrodynamics of Moving Bodies",
      "authors": ["Einstein"],
      "publication_year": 1905,
      "field": "Physics",
      "key_concepts": ["Electrodynamics", "Maxwell's equations", ...]
    }
  ]
}
```

**POST /chat** (with structured sources):
```json
{
  "response": "The core idea of special relativity is...",
  "intent_used": "EXPLAIN",
  "sources": [
    {
      "episode_id": "ep01",
      "episode_title": "Einstein's Special Relativity",
      "start_time": 690.0,
      "end_time": 780.0,
      "timestamp_formatted": "11:30 - 13:00",
      "text_excerpt": "Speed is nothing but distance divided by time...",
      "score": 0.89
    }
  ]
}
```

### Appendix B: File Mapping Reference

Episode ID → Filename mapping (from manifest):
```
ep01 → Great Papers 01 - Einstein_s Special Relativity.mp3
ep02 → Great Papers 02 - How Black Holes Radiate, Hawking 1975.mp3
...
```

### Appendix C: Timestamp Format Conversion

Backend stores: `start_time: 690.0` (seconds)  
Frontend displays: `"11:30"` (MM:SS)

```typescript
function formatTimestamp(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}
```

---

**End of Assessment**

**Status:** Ready for design phase  
**Next Document:** `.kiro/specs/frontend-implementation/design.md`
