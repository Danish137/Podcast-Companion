# Frontend Implementation Requirements

## Introduction

This specification defines the requirements for implementing a web-based frontend for the Fermi Companion learning assistant. The frontend will provide a conversational interface for learners to explore landmark scientific papers through the supplied Fermi Podcast audio collection, with strong emphasis on source verification and trustworthy grounded learning.

## Glossary

- **Frontend Application**: The web-based user interface built with React that enables learners to interact with the Fermi Companion system
- **Backend API**: The existing FastAPI service at `/chat` and other endpoints that processes learner queries
- **Episode**: A single podcast episode from the Great Papers series discussing one landmark scientific paper
- **Source Evidence**: Timestamped transcript segments that support assistant responses
- **Session**: A persistent conversation context between the learner and the companion
- **Episode Manifest**: A JSON catalogue containing metadata for all available episodes
- **Chunk**: A retrieval-ready segment of transcript with provenance (episode ID, timestamps, text)
- **Intent**: The classified type of learner query (EXPLAIN, COMPARE, DISCOVER, UNSUPPORTED)
- **Structured Sources**: API response objects containing episode metadata, timestamps, and excerpts (not embedded in markdown)

## Requirements

### Requirement 1: Conversational Learning Interface

**User Story:** As a learner, I want to ask natural-language questions about scientific concepts in the podcast collection, so that I can understand difficult ideas through conversation.

#### Acceptance Criteria

1. WHEN THE learner submits a question, THE Frontend Application SHALL transmit the question to the Backend API endpoint `/chat` with a valid session identifier
2. WHEN THE Backend API returns a response, THE Frontend Application SHALL display the assistant's answer in a readable format with proper typography
3. WHEN THE learner asks a follow-up question, THE Frontend Application SHALL maintain the session context by sending the same session identifier
4. WHERE THE assistant answer contains mathematical notation or scientific terminology, THE Frontend Application SHALL render the content with appropriate formatting
5. WHEN THE Backend API returns an error status, THE Frontend Application SHALL display a user-friendly error message without exposing technical details

### Requirement 2: Source Verification

**User Story:** As a learner, I want to see which episode and timestamp supports each answer, so that I can verify claims against the actual podcast audio.

#### Acceptance Criteria

1. WHEN THE Backend API provides structured source evidence, THE Frontend Application SHALL display episode title, timestamp range, and relevant transcript excerpt for each source
2. WHERE THE Backend API provides audio access, THE Frontend Application SHALL enable the learner to play audio starting from the source timestamp
3. WHEN THE learner clicks on a source reference, THE Frontend Application SHALL navigate to or highlight the corresponding source evidence
4. THE Frontend Application SHALL NOT parse markdown citations with regular expressions to extract source metadata
5. WHERE THE Backend API returns multiple sources, THE Frontend Application SHALL visually distinguish between different episodes

### Requirement 3: Conversational Discovery

**User Story:** As a learner, I want to discover relevant material through natural conversation, so that I can find content without browsing an episode catalogue.

#### Acceptance Criteria

1. WHEN THE learner asks a discovery question, THE Frontend Application SHALL transmit the question to the Backend API using the same `/chat` endpoint as other queries
2. WHEN THE Backend API returns conversational recommendations, THE Frontend Application SHALL display the response as a natural conversational answer without switching to a browse mode
3. THE Frontend Application SHALL NOT present an episode catalogue, grid, or list as primary navigation
4. THE Frontend Application SHALL NOT require the learner to select an episode before asking a question
5. WHERE THE companion's answer mentions specific episodes or papers, THE Frontend Application SHALL display those mentions as part of the conversational response text

### Requirement 4: Session Management

**User Story:** As a learner, I want my conversation to maintain context across multiple questions, so that I can have a natural dialogue without repeating myself.

#### Acceptance Criteria

1. WHEN THE learner starts a new conversation, THE Frontend Application SHALL generate a unique session identifier using a standard UUID format
2. THE Frontend Application SHALL persist the session identifier in browser storage during the conversation lifetime
3. WHEN THE learner creates a new conversation, THE Frontend Application SHALL generate a new session identifier and reset the conversation display
4. THE Frontend Application SHALL NOT assume conversation state persists across backend restarts unless the Backend API explicitly provides session persistence
5. WHEN THE Frontend Application sends a chat request, THE Frontend Application SHALL include the current session identifier in the request body

### Requirement 5: Intent-Aware Experience

**User Story:** As a learner, I want the interface to adapt to different types of questions (explanations, comparisons, discoveries), so that the presentation matches my learning need.

#### Acceptance Criteria

1. WHEN THE Backend API returns a comparison response with sources from multiple episodes, THE Frontend Application SHALL visually organize sources by episode to preserve per-episode provenance
2. WHEN THE Backend API returns a discovery response, THE Frontend Application SHALL present recommended episodes in a format that emphasizes episode metadata over transcript excerpts
3. WHEN THE Backend API classifies a query as UNSUPPORTED, THE Frontend Application SHALL render the refusal as an intentional trustworthy response without displaying generic error UI
4. WHERE THE Backend API returns contextual follow-up suggestions, THE Frontend Application SHALL display actionable follow-up options relevant to the current answer
5. THE Frontend Application SHALL NOT display internal intent classification details or retrieval pipeline implementation to the learner

### Requirement 6: Responsive Layout

**User Story:** As a learner, I want the interface to work on both desktop and mobile devices, so that I can study in different contexts.

#### Acceptance Criteria

1. WHEN THE learner accesses the Frontend Application on a desktop viewport, THE Frontend Application SHALL display conversation and episode catalogue in a two-column layout
2. WHEN THE learner accesses the Frontend Application on a mobile viewport, THE Frontend Application SHALL collapse the layout into a single column without horizontal overflow
3. WHERE THE viewport width is below 768 pixels, THE Frontend Application SHALL adapt navigation controls for touch interaction
4. THE Frontend Application SHALL maintain readable text size across viewport sizes without requiring horizontal scrolling
5. WHEN THE learner rotates a mobile device, THE Frontend Application SHALL reflow the layout without losing conversation position

### Requirement 7: Audio Playback

**User Story:** As a learner, I want to listen to the podcast audio at the exact timestamp mentioned in a source, so that I can verify the assistant's answer.

#### Acceptance Criteria

1. WHERE THE Backend API exposes episode audio, THE Frontend Application SHALL provide an audio player component
2. WHEN THE learner clicks "Listen from [timestamp]" on a source card, THE Frontend Application SHALL load the episode audio and seek to the specified start timestamp
3. THE Frontend Application SHALL display current playback position and total duration
4. THE Frontend Application SHALL NOT build a full-featured podcast application with playlists or subscription features
5. WHERE THE Backend API cannot provide audio access, THE Frontend Application SHALL degrade gracefully by displaying timestamp information without fake playback controls

### Requirement 8: Loading and Error States

**User Story:** As a learner, I want to understand what the system is doing while I wait, so that I know the application is working.

#### Acceptance Criteria

1. WHEN THE Frontend Application submits a question to the Backend API, THE Frontend Application SHALL display a loading indicator with meaningful status text
2. THE Frontend Application SHALL NOT display loading text that misrepresents actual Backend API behavior
3. WHEN THE Backend API returns a 500 error, THE Frontend Application SHALL display a retry option while preserving the existing conversation
4. WHERE THE Backend API request times out, THE Frontend Application SHALL inform the learner and provide a retry action
5. THE Frontend Application SHALL NOT leave the interface in a blank loading state for more than 5 seconds without feedback

### Requirement 9: Empty State Experience

**User Story:** As a new learner, I want to understand what the companion can do when I first arrive, so that I know how to start.

#### Acceptance Criteria

1. WHEN THE learner first loads the Frontend Application with no active conversation, THE Frontend Application SHALL display an introductory message explaining the companion's purpose
2. THE Frontend Application SHALL provide example questions that demonstrate different capabilities
3. WHERE THE learner has not yet asked a question, THE Frontend Application SHALL suggest trying explanation, comparison, or discovery queries
4. THE Frontend Application SHALL make the conversation input field prominent and accessible on the initial screen
5. THE Frontend Application SHALL NOT require the learner to navigate through multiple screens before asking a question

### Requirement 10: Accessibility

**User Story:** As a learner using assistive technology, I want the interface to work with keyboard navigation and screen readers, so that I can learn effectively.

#### Acceptance Criteria

1. THE Frontend Application SHALL enable keyboard navigation to all interactive elements including input field, buttons, and source cards
2. WHERE THE learner focuses on an interactive element, THE Frontend Application SHALL display a visible focus indicator
3. THE Frontend Application SHALL provide semantic HTML labels for all form controls and interactive elements
4. WHERE THE Frontend Application displays audio controls, THE Frontend Application SHALL expose playback state to assistive technologies
5. THE Frontend Application SHALL maintain readable contrast ratios of at least 4.5:1 for body text and 3:1 for large text
