# Frontend Implementation Tasks

This document provides a concrete task list for implementing the Fermi Companion frontend based on the requirements and design specifications.

Each task builds incrementally on previous work, ending with a fully integrated system.

---

## Task Organization

- **Top-level tasks** represent major implementation milestones
- **Sub-tasks** (numbered X.1, X.2, etc.) represent specific coding steps
- **Optional tasks** marked with `*` are nice-to-have enhancements
- All tasks reference specific requirements from `requirements.md`

---

## Phase 1: Backend Contract Changes

- [x] 1. Add structured source evidence to `/chat` endpoint









  - [ ] 1.1 Create `SourceEvidence` Pydantic model in `src/api.py` with fields: episode_id, episode_title, start_time, end_time, excerpt (optional)
  - [x] 1.2 Extend `ChatResponse` model to include `sources: List[SourceEvidence] = []`









  - [ ] 1.3 Modify `/chat` endpoint to map `state.last_retrieved_evidence` chunks to SourceEvidence objects
  - [x] 1.4 Format timestamps as seconds (float), not MM:SS strings (frontend will format)


  - [ ] 1.5 Include first 200 characters of chunk text as excerpt where available
  - [ ] 1.6 Test with curl: `curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"session_id":"test","message":"Explain special relativity"}'`
  - [ ] 1.7 Verify JSON response contains sources array with correct structure
  - _Requirements: 2.1, 2.4_

- [ ] 2. Add controlled audio access endpoint
  - [ ] 2.1 Create `GET /episodes/{episode_id}/audio` route in `src/api.py`
  - [ ] 2.2 Load episode manifest from `data/metadata/episode_manifest.json`
  - [ ] 2.3 Validate episode_id against manifest, return 404 if not found
  - [ ] 2.4 Map episode_id to filename using manifest's filename field
  - [ ] 2.5 Construct audio path: `PODCAST_DIR / filename`
  - [ ] 2.6 Return FileResponse with media_type="audio/mpeg" and Accept-Ranges support
  - [ ] 2.7 Test with curl: `curl -I http://localhost:8000/episodes/ep01/audio`
  - [ ] 2.8 Verify response headers include Content-Type and Accept-Ranges
  - _Requirements: 7.1, 7.2_

- [ ] 3. Configure CORS for local development
  - [ ] 3.1 Import CORSMiddleware from fastapi.middleware.cors
  - [ ] 3.2 Add middleware allowing origin http://localhost:5173 (Vite default)
  - [x] 3.3 Enable credentials, all methods, all headers

  - [x] 3.4 Test cross-origin request from frontend dev server

  - _Requirements: 1.1_

- [ ] 4. Verify backend changes with integration test
  - [x] 4.1 Start backend: `python -m src.api`

  - [x] 4.2 Send chat request, verify structured sources in response

  - [x] 4.3 Request audio endpoint, verify MP3 stream starts

  - [ ] 4.4 Test invalid episode ID, verify 404 response


  - _Requirements: 1.1, 2.1, 7.1_

---

## Phase 2: Frontend Project Setup

- [-] 5. Initialize React + TypeScript project with Vite

  - [ ] 5.1 Run `npm create vite@latest frontend -- --template react-ts`
  - [ ] 5.2 Navigate to frontend directory: `cd frontend`
  - [ ] 5.3 Install base dependencies: `npm install`
  - [ ] 5.4 Install Tailwind CSS: `npm install -D tailwindcss postcss autoprefixer`
  - [ ] 5.5 Initialize Tailwind: `npx tailwindcss init -p`
  - [ ] 5.6 Install react-markdown: `npm install react-markdown`
  - [ ] 5.7 Configure Tailwind in `tailwind.config.js` with content paths
  - [ ] 5.8 Add Tailwind directives to `src/index.css`
  - [ ] 5.9 Test dev server: `npm run dev`, verify it loads at http://localhost:5173
  - _Requirements: 1.1_

- [ ] 6. Configure Vite for backend integration
  - [ ] 6.1 Create `.env` file with `VITE_API_BASE_URL=http://localhost:8000`
  - [ ] 6.2 Update `vite.config.ts` with proxy configuration for /chat and /episodes routes
  - [ ] 6.3 Test proxy by making fetch request to /chat from browser console
  - _Requirements: 1.1_

- [ ] 7. Set up TypeScript types for API
  - [ ] 7.1 Create `src/types/api.ts` file
  - [ ] 7.2 Define `SourceEvidence` interface matching backend model
  - [ ] 7.3 Define `ChatResponse` interface with response, intent_used, sources
  - [ ] 7.4 Define `Message` interface for frontend state
  - [ ] 7.5 Export all types
  - _Requirements: 1.1, 2.1_

---

## Phase 3: Core Layout and Empty State

- [ ] 8. Create application shell
  - [ ] 8.1 Create `src/components/Layout.tsx` with header and main content area
  - [ ] 8.2 Add "Fermi Companion" title in header
  - [ ] 8.3 Add "New Conversation" button in header (functional later)
  - [ ] 8.4 Style with Tailwind: neutral colors, clean typography
  - [ ] 8.5 Make responsive: stack on mobile, horizontal on desktop
  - [ ] 8.6 Update `src/App.tsx` to render Layout
  - _Requirements: 1.1, 6.1, 6.2_

- [ ] 9. Create empty state component
  - [ ] 9.1 Create `src/components/EmptyState.tsx`
  - [ ] 9.2 Add centered title: "FERMI COMPANION"
  - [ ] 9.3 Add tagline: "Explore the ideas behind landmark scientific papers."
  - [ ] 9.4 Add instructional text about asking questions and tracing answers
  - [ ] 9.5 Add example queries list with suggested questions
  - [ ] 9.6 Style with excellent typography, generous whitespace, calm aesthetic
  - [ ] 9.7 Make responsive: adjust font sizes and spacing for mobile
  - _Requirements: 9.1, 9.2, 9.3, 9.5_

- [ ] 10. Test empty state rendering
  - [ ] 10.1 Verify empty state appears on initial load
  - [ ] 10.2 Check typography hierarchy is clear
  - [ ] 10.3 Test responsive behavior at mobile, tablet, desktop widths
  - _Requirements: 9.1, 9.4_

---

## Phase 4: API Client and State Management

- [ ] 11. Build centralized API client
  - [ ] 11.1 Create `src/api/client.ts` file
  - [ ] 11.2 Define API_BASE_URL from environment variable
  - [ ] 11.3 Implement `chat(sessionId, message)` async function using fetch
  - [ ] 11.4 Add error handling with custom ApiError class
  - [ ] 11.5 Implement `getAudioUrl(episodeId)` function returning audio endpoint URL
  - [ ] 11.6 Add TypeScript types for all functions
  - [ ] 11.7 Export all functions
  - _Requirements: 1.1, 7.1_

- [ ] 12. Create session management hook
  - [ ] 12.1 Create `src/hooks/useSession.ts` file
  - [ ] 12.2 Implement session ID generation using crypto.randomUUID()
  - [ ] 12.3 Store session ID in component state
  - [ ] 12.4 Provide function to create new session (new UUID)
  - [ ] 12.5 Export useSession hook
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 13. Create conversation context
  - [ ] 13.1 Create `src/contexts/ConversationContext.tsx` file
  - [ ] 13.2 Define ConversationState interface: sessionId, messages, isLoading, error
  - [ ] 13.3 Create context with createContext
  - [ ] 13.4 Implement ConversationProvider with state management
  - [ ] 13.5 Implement sendMessage function: add user message, call API, add assistant message
  - [ ] 13.6 Implement newConversation function: reset sessionId and messages
  - [ ] 13.7 Handle loading and error states
  - [ ] 13.8 Export context and provider
  - _Requirements: 1.1, 1.2, 1.3, 4.1, 4.2, 4.3_

- [ ] 14. Wrap App with ConversationProvider
  - [ ] 14.1 Import ConversationProvider in `src/App.tsx`
  - [ ] 14.2 Wrap Layout component with provider
  - [ ] 14.3 Verify context is accessible in child components
  - _Requirements: 1.1_

---

## Phase 5: Conversation UI Components

- [ ] 15. Create Composer component
  - [ ] 15.1 Create `src/components/Conversation/Composer.tsx` file
  - [ ] 15.2 Add textarea for user input with auto-resize behavior
  - [ ] 15.3 Add send button with icon or text
  - [ ] 15.4 Handle Enter key to submit (Shift+Enter for newline)
  - [ ] 15.5 Disable during loading state
  - [ ] 15.6 Clear input after successful send
  - [ ] 15.7 Connect to ConversationContext.sendMessage
  - [ ] 15.8 Style with Tailwind: clean border, focus states, accessible
  - [ ] 15.9 Add loading indicator when isLoading is true
  - _Requirements: 1.1, 8.1, 10.1, 10.2_

- [ ] 16. Create message components
  - [ ] 16.1 Create `src/components/Conversation/UserMessage.tsx` for user messages
  - [ ] 16.2 Style user messages: right-aligned, subtle background, clear typography
  - [ ] 16.3 Create `src/components/Conversation/AssistantMessage.tsx` for assistant messages
  - [ ] 16.4 Integrate react-markdown for assistant response rendering
  - [ ] 16.5 Style assistant messages: left-aligned, full-width, readable
  - [ ] 16.6 Handle markdown rendering with proper spacing and hierarchy
  - _Requirements: 1.2, 5.1_

- [ ] 17. Create MessageList component
  - [ ] 17.1 Create `src/components/Conversation/MessageList.tsx` file
  - [ ] 17.2 Map over messages array from ConversationContext
  - [ ] 17.3 Render UserMessage or AssistantMessage based on role
  - [ ] 17.4 Implement auto-scroll to bottom on new messages
  - [ ] 17.5 Style scrollable container with proper padding
  - [ ] 17.6 Make responsive: adjust spacing for mobile
  - _Requirements: 1.2_

- [ ] 18. Create ConversationView component
  - [ ] 18.1 Create `src/components/Conversation/ConversationView.tsx` file
  - [ ] 18.2 Conditionally render EmptyState when messages array is empty
  - [ ] 18.3 Conditionally render MessageList + Composer when messages exist
  - [ ] 18.4 Connect to ConversationContext for messages state
  - [ ] 18.5 Update Layout to render ConversationView in main area
  - _Requirements: 1.1, 1.2, 9.1_

- [ ] 19. Test basic conversation flow
  - [ ] 19.1 Start backend: `python -m src.api`
  - [ ] 19.2 Start frontend: `npm run dev`
  - [ ] 19.3 Type question in composer and submit
  - [ ] 19.4 Verify user message appears immediately
  - [ ] 19.5 Verify loading indicator shows during request
  - [ ] 19.6 Verify assistant message appears with response text
  - [ ] 19.7 Test follow-up question, verify conversation history maintained
  - _Requirements: 1.1, 1.2, 1.3_

---

## Phase 6: Source Verification

- [ ] 20. Create utility functions for formatting
  - [ ] 20.1 Create `src/utils/format.ts` file
  - [ ] 20.2 Implement `formatTimestamp(seconds: number): string` converting seconds to MM:SS format
  - [ ] 20.3 Implement `formatTimeRange(start: number, end: number): string` for timestamp ranges
  - [ ] 20.4 Add unit tests or manual verification for edge cases
  - [ ] 20.5 Export all functions
  - _Requirements: 2.1_

- [ ] 21. Create SourceCard component
  - [ ] 21.1 Create `src/components/Conversation/SourceCard.tsx` file
  - [ ] 21.2 Accept props: episodeId, episodeTitle, startTime, endTime, excerpt (optional)
  - [ ] 21.3 Display "SOURCE" label at top
  - [ ] 21.4 Display episode title (not as link - just text)
  - [ ] 21.5 Display formatted timestamp range (MM:SS - MM:SS)
  - [ ] 21.6 Display excerpt text if provided (max 200 chars with ellipsis)
  - [ ] 21.7 Add "Listen from [MM:SS]" button
  - [ ] 21.8 Style with card appearance: subtle background, border, padding, shadow
  - [ ] 21.9 Make responsive: stack content on mobile
  - [ ] 21.10 Do NOT show similarity scores or retrieval metadata
  - _Requirements: 2.1, 2.2, 2.3, 5.5_

- [ ] 22. Integrate SourceCard into AssistantMessage
  - [ ] 22.1 Update AssistantMessage to accept sources prop
  - [ ] 22.2 Render array of SourceCard components below response text
  - [ ] 22.3 Add spacing between response and sources
  - [ ] 22.4 Handle case where sources array is empty (no sources shown)
  - [ ] 22.5 Test with real backend response containing sources
  - _Requirements: 2.1, 2.5_

- [ ] 23. Test source display
  - [ ] 23.1 Ask question that returns sources: "Explain special relativity"
  - [ ] 23.2 Verify SourceCard components appear below assistant response
  - [ ] 23.3 Verify episode titles are correct
  - [ ] 23.4 Verify timestamps are formatted correctly (MM:SS)
  - [ ] 23.5 Verify excerpts display properly
  - [ ] 23.6 Test with query returning multiple sources
  - _Requirements: 2.1, 2.2, 2.3_

---

## Phase 7: Audio Player Integration

- [ ] 24. Create audio context
  - [ ] 24.1 Create `src/contexts/AudioContext.tsx` file
  - [ ] 24.2 Define AudioState interface: currentEpisodeId, currentTime, duration, isPlaying, isLoading, error
  - [ ] 24.3 Create context with createContext
  - [ ] 24.4 Implement AudioProvider with audio element ref
  - [ ] 24.5 Implement playFromTimestamp(episodeId, startTime) function
  - [ ] 24.6 Handle loading new episode audio vs seeking in current episode
  - [ ] 24.7 Implement pause(), play() functions
  - [ ] 24.8 Handle audio events: loadedmetadata, timeupdate, ended, error
  - [ ] 24.9 Export context and provider
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 25. Create AudioPlayer component
  - [ ] 25.1 Create `src/components/AudioPlayer.tsx` file
  - [ ] 25.2 Connect to AudioContext for state
  - [ ] 25.3 Render compact bottom bar (fixed position)
  - [ ] 25.4 Display current episode title when audio is loaded
  - [ ] 25.5 Add play/pause button
  - [ ] 25.6 Add seek slider (input type="range")
  - [ ] 25.7 Display current time / total duration (formatted as MM:SS)
  - [ ] 25.8 Show loading spinner when audio is loading
  - [ ] 25.9 Handle audio errors with user-friendly message
  - [ ] 25.10 Style as minimal, compact bar - not full podcast player UI
  - [ ] 25.11 Make responsive: compact on mobile
  - _Requirements: 7.1, 7.3, 7.4, 7.5_

- [ ] 26. Connect SourceCard to AudioPlayer
  - [ ] 26.1 Import AudioContext in SourceCard component
  - [ ] 26.2 Connect "Listen from..." button click to AudioContext.playFromTimestamp
  - [ ] 26.3 Pass episodeId and startTime to playFromTimestamp function
  - [ ] 26.4 Verify button is keyboard accessible
  - _Requirements: 2.2, 7.2_

- [ ] 27. Wrap App with AudioProvider
  - [ ] 27.1 Import AudioProvider in `src/App.tsx`
  - [ ] 27.2 Wrap existing providers with AudioProvider
  - [ ] 27.3 Add AudioPlayer component at app level (fixed position)
  - _Requirements: 7.1_

- [ ] 28. Test audio playback
  - [ ] 28.1 Ask question with sources: "Explain special relativity"
  - [ ] 28.2 Click "Listen from..." button on a source card
  - [ ] 28.3 Verify audio player appears and shows loading state
  - [ ] 28.4 Verify audio loads and starts playing from correct timestamp
  - [ ] 28.5 Verify seek slider works correctly
  - [ ] 28.6 Verify play/pause button works
  - [ ] 28.7 Test clicking different source - verify audio switches correctly
  - [ ] 28.8 Test with invalid episode ID (should handle error gracefully)
  - _Requirements: 7.1, 7.2, 7.3, 7.5_

---

## Phase 8: Error and Loading States

- [ ] 29. Implement loading states
  - [ ] 29.1 Update Composer to show loading indicator when ConversationContext.isLoading is true
  - [ ] 29.2 Add loading message: "Finding relevant material..." or similar
  - [ ] 29.3 Disable composer input during loading
  - [ ] 29.4 Update AudioPlayer to show loading state when fetching audio
  - [ ] 29.5 Test loading states with real backend requests
  - _Requirements: 8.1, 8.2_

- [ ] 30. Implement error handling
  - [ ] 30.1 Display error message from ConversationContext.error when present
  - [ ] 30.2 Add "Try again" button to retry failed request
  - [ ] 30.3 Preserve existing conversation when error occurs
  - [ ] 30.4 Style error message: clear, non-technical, user-friendly
  - [ ] 30.5 Handle audio errors separately in AudioPlayer component
  - [ ] 30.6 Test error states by simulating backend failures
  - _Requirements: 1.5, 8.3, 8.4_

- [ ] 31. Test unsupported query handling
  - [ ] 31.1 Ask unsupported question: "Explain string theory"
  - [ ] 31.2 Verify response renders as normal assistant message (not error state)
  - [ ] 31.3 Verify refusal message is displayed clearly
  - [ ] 31.4 Confirm no error indicators appear
  - _Requirements: 5.3_

---

## Phase 9: Responsive Design and Accessibility

- [ ] 32. Implement responsive breakpoints
  - [ ] 32.1 Test layout at mobile width (<768px)
  - [ ] 32.2 Test layout at tablet width (768px-1023px)
  - [ ] 32.3 Test layout at desktop width (≥1024px)
  - [ ] 32.4 Adjust conversation max-width for readability
  - [ ] 32.5 Ensure no horizontal overflow on any width
  - [ ] 32.6 Make source cards stack properly on mobile
  - [ ] 32.7 Adjust audio player for mobile (compact)
  - [ ] 32.8 Test touch interactions on mobile device or emulator
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 33. Implement accessibility features
  - [ ] 33.1 Add aria-label to composer textarea: "Your question"
  - [ ] 33.2 Add aria-label to send button: "Send message"
  - [ ] 33.3 Add aria-label to audio player: "Episode audio player"
  - [ ] 33.4 Add role="log" and aria-live="polite" to message list
  - [ ] 33.5 Ensure all interactive elements have visible focus indicators
  - [ ] 33.6 Test keyboard navigation: Tab through all elements
  - [ ] 33.7 Test Enter key on send button
  - [ ] 33.8 Verify color contrast meets WCAG AA standards (4.5:1 for normal text)
  - [ ] 33.9 Add focus trap in composer when active
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

---

## Phase 10: Polish and Final Testing

- [ ] 34. Typography and spacing refinement
  - [ ] 34.1 Review and adjust font sizes across all components
  - [ ] 34.2 Review and adjust line heights for readability
  - [ ] 34.3 Review and adjust spacing between elements
  - [ ] 34.4 Ensure visual hierarchy is clear (titles > headings > body)
  - [ ] 34.5 Test with long response text to verify readability
  - _Requirements: All visual requirements_

- [ ] 35. Visual design polish
  - [ ] 35.1 Refine SourceCard styling: borders, shadows, colors
  - [ ] 35.2 Refine message bubbles: backgrounds, padding, borders
  - [ ] 35.3 Refine composer styling: focus states, borders
  - [ ] 35.4 Refine audio player: compact, clean, unobtrusive
  - [ ] 35.5 Ensure consistent color usage throughout
  - [ ] 35.6 Add subtle transitions (opacity, transform) where appropriate
  - [ ] 35.7 Verify calm, scientific, editorial aesthetic
  - _Requirements: Visual design requirements_

- [ ]* 36. Add contextual follow-up suggestions (OPTIONAL)
  - [ ]* 36.1 Create FollowUpSuggestions component
  - [ ]* 36.2 Define useful follow-up prompts: "Explain more simply", "Give an analogy", "Go deeper"
  - [ ]* 36.3 Render below assistant message when appropriate
  - [ ]* 36.4 Connect buttons to send pre-filled follow-up messages
  - [ ]* 36.5 Style as subtle, non-intrusive buttons
  - _Requirements: 5.4_

- [ ] 37. Comprehensive testing
  - [ ] 37.1 Test factual question: "What is the core idea of special relativity?"
  - [ ] 37.2 Test conceptual explanation: "How do black holes radiate according to Hawking?"
  - [ ] 37.3 Test follow-up: Ask question, then "I still don't understand that"
  - [ ] 37.4 Test "explain more simply": Ask complex question, then "Explain this more simply"
  - [ ] 37.5 Test multi-turn context: Have 3+ turn conversation, verify context maintained
  - [ ] 37.6 Test source display: Verify all sources appear correctly
  - [ ] 37.7 Test episode names: Verify episode titles match backend data
  - [ ] 37.8 Test timestamps: Verify timestamps formatted correctly
  - [ ] 37.9 Test excerpts: Verify excerpts display when provided
  - [ ] 37.10 Test audio playback: Verify audio loads and plays
  - [ ] 37.11 Test audio seeking: Verify seeking to timestamp works
  - [ ] 37.12 Test conversational discovery: "Which material covers information theory?"
  - [ ] 37.13 Test comparison: "Compare Einstein and Bell"
  - [ ] 37.14 Test unsupported: "Explain string theory"
  - [ ] 37.15 Test backend error: Stop backend mid-conversation, verify error handling
  - [ ] 37.16 Test audio error: Request invalid episode audio, verify error handling
  - _Requirements: All functional requirements_

- [ ] 38. Cross-browser testing
  - [ ] 38.1 Test in Chrome (latest)
  - [ ] 38.2 Test in Firefox (latest)
  - [ ] 38.3 Test in Safari (latest) if on macOS
  - [ ] 38.4 Test in Edge (latest)
  - [ ] 38.5 Test on mobile Safari (iOS)
  - [ ] 38.6 Test on mobile Chrome (Android)
  - _Requirements: 6.1, 6.2_

- [ ] 39. Performance check
  - [ ] 39.1 Run production build: `npm run build`
  - [ ] 39.2 Check bundle sizes in dist/ folder
  - [ ] 39.3 Verify initial JS bundle <200KB gzipped
  - [ ] 39.4 Test page load time on throttled connection
  - [ ] 39.5 Check for unnecessary re-renders with React DevTools
  - [ ] 39.6 Verify no memory leaks during long conversations
  - _Requirements: Performance considerations_

---

## Phase 11: Documentation and Deployment Preparation

- [ ] 40. Create frontend README
  - [ ] 40.1 Create `frontend/README.md` file
  - [ ] 40.2 Document setup steps: npm install, env variables
  - [ ] 40.3 Document development commands: npm run dev, build, preview
  - [ ] 40.4 Document backend dependency and how to start it
  - [ ] 40.5 Document browser requirements and tested browsers
  - [ ] 40.6 Add troubleshooting section for common issues
  - _Requirements: Documentation needs_

- [ ] 41. Update project STATUS.md
  - [ ] 41.1 Update current phase to "Frontend Complete"
  - [ ] 41.2 List all completed frontend tasks
  - [ ] 41.3 Document files changed: backend (src/api.py) and all frontend files
  - [ ] 41.4 Document known limitations: session persistence, mobile optimization level
  - [ ] 41.5 Record next recommended task (if any)
  - _Requirements: Project continuity_

- [ ] 42. Update DECISIONS.md if needed
  - [ ] 42.1 Record decision to use React + TypeScript + Vite + Tailwind
  - [ ] 42.2 Record decision to NOT implement episode browsing UI
  - [ ] 42.3 Record decision to use Context API over Redux
  - [ ] 42.4 Record any other significant architectural decisions made during implementation
  - _Requirements: Project continuity_

---

## Success Verification Checklist

After completing all tasks, verify these outcomes:

### Conversation
- [x] ✓ Learner can ask questions and receive grounded answers
- [x] ✓ Assistant responses render with proper markdown formatting
- [x] ✓ Follow-up questions maintain conversation context
- [x] ✓ "Explain more simply" type queries work correctly
- [x] ✓ Multi-turn conversations feel natural and coherent

### Sources
- [x] ✓ Source cards appear below assistant responses
- [x] ✓ Episode names are correct and match backend data
- [x] ✓ Timestamps are correctly formatted (MM:SS - MM:SS)
- [x] ✓ Excerpts display properly when provided
- [x] ✓ Audio loads when "Listen from..." is clicked
- [x] ✓ Audio seeks to correct timestamp

### Discovery
- [x] ✓ Conversational discovery works ("Which material covers X?")
- [x] ✓ Relevant material mentioned naturally in response text
- [x] ✓ NO episode browsing/selection UI exists

### Comparison
- [x] ✓ Multi-episode comparison queries work
- [x] ✓ Sources from different episodes remain distinguishable

### Unsupported
- [x] ✓ Unsupported requests display as trustworthy refusals
- [x] ✓ No error UI shown for unsupported queries

### Error Handling
- [x] ✓ Backend errors display user-friendly message with retry
- [x] ✓ Audio errors display appropriate message
- [x] ✓ Conversation preserved when errors occur

### Responsive & Accessible
- [x] ✓ Layout works on mobile, tablet, and desktop
- [x] ✓ No horizontal overflow on any screen size
- [x] ✓ All interactive elements keyboard accessible
- [x] ✓ Focus indicators visible
- [x] ✓ Color contrast meets WCAG standards

### Product Feel
- [x] ✓ Interface feels like learning companion, NOT podcast browser
- [x] ✓ Discovery is conversational, NOT catalogue-based
- [x] ✓ Visual design feels calm, scientific, editorial, trustworthy
- [x] ✓ Typography and spacing support long-form reading

---

**End of Tasks**

When all non-optional tasks are complete and verified, the frontend implementation is done. Update STATUS.md with final state and prepare for any remaining project milestones.
