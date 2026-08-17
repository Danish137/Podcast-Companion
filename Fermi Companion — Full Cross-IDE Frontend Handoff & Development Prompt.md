# Fermi Companion — Full Cross-IDE Frontend Handoff & Development Prompt

You are taking over an existing AI engineering project from another coding environment.

This is NOT a greenfield project.

The previous coding agent has already implemented the backend, ingestion, transcription, retrieval, conversation logic, evaluation system, and other core functionality.

Your job is now to:

1. reconstruct the actual project state from the repository;
2. verify that the documented state matches the code;
3. inspect the existing implementation deeply;
4. improve the proposed frontend integration approach where the existing architecture allows a better solution;
5. make the minimal backend/API changes required for a high-quality frontend;
6. then build the intended frontend experience.

Do NOT rely on previous chat history.

The repository is the persistent project memory.

---

# 1. FIRST: READ THE PROJECT DOCUMENTATION

Before modifying anything, read:

1. `AGENTS.md`
2. `STATUS.md`
3. `DECISIONS.md`
4. `PROJECT_SPEC.md`
5. `PRODUCT.md`
6. `ARCHITECTURE.md`
7. `EVALUATION.md`
8. `IMPLEMENTATION_PLAN.md`
9. `DEVELOPMENT_PROTOCOL.md`

Then inspect the complete repository.

Do not assume the documentation is perfectly accurate.

The documentation represents intended/project state.

The actual source code, configuration, generated artifacts, and executed checks establish what is actually true.

If documentation and implementation disagree:

1. identify the discrepancy;
2. inspect the implementation;
3. determine which behavior is actually current;
4. report it;
5. update `STATUS.md` appropriately.

Do not silently rewrite the architecture based only on documentation.

---

# 2. PROJECT CONTEXT

The project is:

# Fermi Companion

A grounded AI learning companion for exploring landmark scientific papers through the supplied Fermi Podcast collection.

The product is NOT merely:

- a transcript viewer;
- a semantic search interface;
- a generic RAG chatbot;
- a one-time summarizer.

The intended learner loop is:

```text
ASK
 ↓
UNDERSTAND
 ↓
VERIFY
 ↓
EXPLORE
```

The learner should be able to:

- ask about difficult ideas discussed in the supplied episodes;
- ask contextual follow-up questions;
- ask for simpler/deeper explanations;
- discover relevant episodes;
- compare ideas across episodes;
- verify answers against the supplied audio;
- navigate to the source timestamp;
- understand when the supplied collection does not contain enough evidence.

The product should feel like a serious learning companion.

---

# 3. ASSIGNMENT CONSTRAINTS

The assignment brief is authoritative for assignment requirements.

Important requirements:

- The system must start from the supplied raw audio.
- You may NOT use YouTube captions/transcripts or another hosting platform's existing transcripts/caption APIs as input.
- Third-party AI APIs and open-source libraries are allowed.
- The system must support a useful natural-language conversation across the supplied episodes.
- Responses must remain faithful to the supplied audio and be checkable against it.
- The experience must do more than display transcripts or provide a one-time summary.
- A runnable evaluation system is required.
- The evaluation set must contain at least 10 varied cases beyond demo examples.
- Raw evaluation inputs and outputs must be preserved.
- The initial system must be evaluated.
- Concrete successes and failures must be manually inspected.
- One meaningful improvement must be made based on observed failures.
- The same evaluation set must be rerun after the improvement.
- The submission must explain what improved, regressed, or remained unresolved.
- The system must have reproducible setup/run instructions.

The rubric is:

- Problem Framing and Product Judgment: 20
- AI Engineering and System Design: 25
- Conversation Quality and Trustworthiness: 20
- Evaluation System and Improvement: 25
- Code Quality and Runability: 10

Do not optimize only for the AI/RAG implementation.

---

# 4. CORPUS DISCREPANCY

There is an explicit discrepancy between the written assignment brief and the actual supplied corpus.

The brief says:

> 3 raw Fermi Podcast audio files, totalling no more than 3 hours.

The actual supplied workspace contains:

- 16 raw podcast episodes;
- approximately 9.6 hours total;
- the Great Papers collection;
- multiple scientific disciplines.

The observed episodes include:

1. Einstein's Special Relativity
2. How Black Holes Radiate, Hawking 1975
3. The Double Helix, Watson and Crick 1953
4. Shannon and the Birth of Information, 1948
5. Attention Is All You Need, 2017
6. General Relativity, Einstein 1915
7. On Computable Numbers, Turing 1936
8. Natural Selection, Darwin and Wallace 1858
9. Bell's Theorem, 1964
10. The Expanding Universe, Hubble 1929
11. The Birth of the Quantum, Planck 1900
12. The Dirac Equation and Antimatter, 1928
13. How DNA Copies Itself, Meselson-Stahl 1958
14. Gödel's Incompleteness Theorems, 1931
15. The Periodic Table, Mendeleev 1869
16. Nash Equilibrium and Game Theory, 1950

Do NOT silently change the assignment requirement from 3 episodes to 16.

The correct project state is:

```text
Written assignment scope:
3 files / <=3 hours

Observed supplied corpus:
16 episodes / ~9.6 hours

Implementation:
supports arbitrary episode count and currently works with the supplied corpus
```

If Fermi later clarifies the intended scope, update `DECISIONS.md`.

Do not invent such clarification.

---

# 5. SOURCE-OF-TRUTH RULE

The supplied raw podcast audio is the source of truth for podcast-derived factual answers.

The provenance chain should remain:

```text
Supplied raw audio
       ↓
Our transcription
       ↓
Timestamped transcript
       ↓
Processed evidence
       ↓
Retrieved evidence
       ↓
LLM answer
       ↓
Frontend source presentation
```

Do NOT introduce external transcripts/captions.

Do NOT allow frontend code to perform an independent retrieval operation.

The frontend should display evidence that came from the same backend retrieval/evidence path used to generate the answer.

---

# 6. IMPORTANT: INSPECT BEFORE IMPLEMENTING

Before making any change, inspect the actual existing implementation in detail.

Specifically inspect:

## Backend

- FastAPI application;
- `api.py`;
- `/chat`;
- request/response models;
- conversation/session state;
- retrieval implementation;
- evidence objects;
- source/timestamp structures;
- episode manifest;
- audio file mapping;
- discovery implementation;
- comparison implementation;
- unsupported handling;
- prompts;
- model/provider abstraction;
- configuration;
- tests.

## Data

Inspect:

- episode manifest;
- transcript artifacts;
- chunks;
- retrieval index;
- source metadata;
- actual audio filenames;
- episode IDs.

## Existing frontend

There may currently be no frontend.

Verify this rather than assuming it.

## CLI

Inspect the existing CLI because it may reveal:

- expected interaction flow;
- response formatting;
- session handling;
- error behavior;
- existing helper functions that could be reused.

---

# 7. DO NOT ASSUME OUR PROPOSED TECHNIQUE IS OPTIMAL

The previous development discussion proposed:

1. structured sources in `/chat`;
2. `GET /episodes`;
3. controlled audio access;
4. frontend rendering from structured data.

This is the intended direction, but it is NOT an immutable implementation prescription.

Inspect the existing code first.

If the current architecture already contains a better mechanism, use it.

For example:

- If retrieval already produces a strong `Evidence` object, expose that directly instead of creating another representation.
- If the episode manifest already has a canonical API/service layer, reuse it instead of adding duplicate logic.
- If audio mapping is already available through an existing helper, reuse it.
- If a response DTO can be extended cleanly, do that rather than introducing another endpoint unnecessarily.
- If the application can serve the frontend and audio cleanly from the same FastAPI process, prefer that over unnecessary infrastructure.
- If a proposed change would duplicate state or create a second source of truth, reject the proposal and use the better existing mechanism.

You are expected to be an engineer reviewing the architecture, not a code generator blindly following a plan.

Before each significant architectural change, answer:

```text
What already exists?
Why isn't it sufficient?
What is the smallest change?
Is there a simpler way using existing abstractions?
```

---

# 8. CURRENT FRONTEND INTEGRATION AUDIT

The previous coding environment inspected the repository and found:

## Current frontend

No frontend currently exists.

The application currently consists of:

- FastAPI backend;
- terminal CLI.

Verify this yourself.

## Existing endpoints

Currently known:

```text
POST /chat
GET /health
```

Verify the actual current routes.

## Current chat request

Known:

```json
{
  "session_id": "string",
  "message": "string"
}
```

Verify the actual schema.

## Current chat response

Known:

```json
{
  "response": "string",
  "intent_used": "string"
}
```

The response currently embeds source citations in markdown such as:

```text
[Episode Title, MM:SS]
```

Verify this against the actual implementation.

## Current conversation state

The backend currently uses an in-memory session dictionary keyed by `session_id`.

Verify this.

The frontend should generate and persist a session ID for the current conversation.

Do not assume conversation persistence survives backend restarts unless the actual implementation proves it does.

---

# 9. STRUCTURED SOURCE INTEGRATION

The previous audit identified an important weakness:

The backend currently exposes source information only inside the markdown answer.

DO NOT solve this by making the frontend parse citations with regex.

That would create a fragile UI/backend contract.

Instead, inspect the actual evidence objects already produced by retrieval and answer generation.

If appropriate, extend `ChatResponse` with a structured source representation.

Conceptually:

```json
{
  "response": "The answer...",
  "intent_used": "EXPLAIN",
  "sources": [
    {
      "episode_id": "great_papers_01",
      "episode_title": "Great Papers 01 - Einstein's Special Relativity",
      "start_time": 1122.0,
      "end_time": 1178.0,
      "timestamp": "18:42",
      "excerpt": "..."
    }
  ]
}
```

This is only conceptual.

Use the actual evidence structures already present.

Do not create duplicate evidence objects if one already exists.

The source object should expose whatever is actually available:

- episode ID;
- episode title;
- start timestamp;
- end timestamp where available;
- relevant excerpt where available;
- audio reference where appropriate.

Rules:

- Never fabricate source metadata.
- Never fabricate timestamps.
- Never fabricate excerpts.
- Never perform a second frontend retrieval.
- Reuse the actual evidence used by the backend.
- Preserve provenance.

If a field is unavailable, make it optional.

Do not invent it merely to satisfy a UI design.

Keep existing markdown citations if useful for backward compatibility, but the frontend should use structured data.

---

# 10. EPISODE CATALOGUE API

The frontend needs a canonical episode catalogue.

Inspect how the existing manifest is loaded and used.

If appropriate, expose:

```text
GET /episodes
```

using the existing manifest/service.

Do NOT create a second frontend-specific manifest.

Do NOT hardcode episode metadata into React.

The response should contain actual available metadata.

Conceptually:

```json
{
  "episodes": [
    {
      "episode_id": "...",
      "title": "...",
      "paper_title": "...",
      "authors": [],
      "year": null,
      "field": "...",
      "concepts": [],
      "summary": "..."
    }
  ]
}
```

This is only an example.

Use the real manifest schema.

Important:

Metadata must retain its provenance/meaning.

Do not fabricate authors, years, fields, paper titles, or concepts.

If something is unknown, preserve it as unknown.

---

# 11. AUDIO ACCESS

The frontend needs to support source verification through the actual podcast audio.

The backend currently does not expose audio URLs according to the previous audit.

Verify this yourself.

If required, add a controlled audio endpoint such as:

```text
GET /episodes/{episode_id}/audio
```

or another clean mechanism based on the existing architecture.

Requirements:

- resolve episode ID through the canonical episode/audio mapping;
- reject unknown episode IDs;
- never accept arbitrary filesystem paths;
- never expose unrelated files;
- return the correct audio content type;
- preserve HTTP range behavior where possible so browser seeking works.

Do not simply expose the entire filesystem.

If an existing audio-serving mechanism is already present, reuse it.

---

# 12. FRONTEND PRODUCT DESIGN

The frontend should NOT look like a generic AI SaaS dashboard.

The conversation is the primary product surface.

The intended experience is:

```text
                 FERMI COMPANION

                 What do you want
                 to understand?

        [ Ask anything about the collection ]

        Explain something
        Compare two ideas
        Find an episode
        Check whether a topic is covered
```

After the first question:

```text
┌───────────────────────────────────────────────────────────┐
│ Fermi Companion                             Explore       │
├───────────────┬───────────────────────────────────────────┤
│ Conversations │                                             │
│               │ You                                         │
│ + New         │ Why did Einstein need special relativity? │
│               │                                             │
│               │ Companion                                   │
│               │                                             │
│               │ Einstein's problem was...                   │
│               │                                             │
│               │ ┌────────────────────────────────────────┐  │
│               │ │ SOURCE                                 │  │
│               │ │ Great Papers 01                         │  │
│               │ │ 18:42 – 19:31                           │  │
│               │ │                                         │  │
│               │ │ ▶ Listen from here                      │  │
│               │ └────────────────────────────────────────┘  │
│               │                                             │
│               │ Explain this more simply                    │
│               │ Give me an analogy                           │
│               │ What should I understand next?               │
│               │                                             │
│               │ [ Ask a follow-up...                    ↑ ] │
└───────────────┴───────────────────────────────────────────┘
```

This is conceptual direction, not a requirement to reproduce the exact wireframe.

Use good product judgment.

---

# 13. FRONTEND DESIGN PRINCIPLES

The interface should feel:

- intelligent;
- calm;
- focused;
- scientific;
- modern;
- trustworthy.

Prefer:

- excellent typography;
- strong whitespace;
- clear hierarchy;
- subtle interaction;
- readable long-form answers;
- restrained source cards;
- thoughtful transitions.

Avoid:

- dashboard aesthetics;
- excessive cards;
- excessive gradients;
- huge hero sections after the conversation begins;
- excessive animation;
- generic "AI SaaS" visual language;
- unnecessary metrics;
- vector-search jargon;
- visible implementation details.

Do not expose:

- embeddings;
- similarity scores;
- retrieval pipeline;
- vector database;
- model names;
- internal intent classifier details.

The learner should care about:

> What did you tell me?

> Why should I trust it?

> Where can I listen to the source?

> What should I ask next?

---

# 14. CONVERSATION EXPERIENCE

The primary screen should support:

- user messages;
- assistant messages;
- loading/streaming if actually supported;
- contextual follow-ups;
- markdown;
- mathematical notation where necessary;
- readable scientific explanations;
- errors;
- retry.

The assistant answer should be visually dominant.

Source evidence should support the answer rather than overwhelm it.

Contextual follow-ups should be useful.

Examples:

- Explain this more simply
- Give me an analogy
- Walk me through the example
- Go deeper
- What should I understand next?

Do not permanently display a large set of buttons.

Only show useful contextual actions.

---

# 15. SOURCE EXPERIENCE

This is one of the most important frontend features.

Do not render a generic citation such as:

> Source: Episode 4

Instead:

```text
SOURCE

Great Papers 04
Shannon and the Birth of Information

18:32 – 19:17

[relevant excerpt]

▶ Listen from 18:32
```

If multiple sources exist, show them clearly.

Where possible, associate sources with the relevant answer section.

If the backend provides no excerpt, do not invent one.

If audio is unavailable, degrade gracefully:

> Source: Great Papers 04 · 18:32

Do not create fake playback controls.

---

# 16. AUDIO PLAYER

If audio access is implemented:

- use the actual supplied audio;
- allow seeking to the source start timestamp;
- show current playback position where useful;
- make source verification easy;
- keep the player compact.

Do NOT build a full podcast app.

The goal is:

> verify the answer against the source.

A source card with:

`Listen from 18:32`

is more important than elaborate playback controls.

---

# 17. EXPLORE EXPERIENCE

Provide a lightweight Explore surface.

The learner should be able to discover:

- episodes;
- topics;
- fields;
- papers;
- years;
- relevant concepts.

Use actual backend metadata.

Example:

```text
Explore the collection

Search by topic, paper, or field

[ information theory                         ]

────────────────────────────────────

Great Papers 04
Shannon and the Birth of Information
1948 · Information Theory

Great Papers 05
Attention Is All You Need
2017 · Computer Science
```

This should complement the conversation.

It should not become a dashboard.

A learner should also be able to return from Explore to a conversation.

---

# 18. COMPARISON EXPERIENCE

Comparison is one of the strongest ways to differentiate the product from generic RAG.

When the backend returns a comparison, make the UI visibly communicate multiple sources.

Conceptually:

```text
How these episodes approach the idea

Einstein
────────────
...

Source
18:42 – 19:31

Bell
────────────
...

Source
22:14 – 23:02

The connection
────────────
...
```

Preserve per-episode provenance.

Do not collapse all evidence into one undifferentiated citation list.

Use the actual backend response structure.

---

# 19. UNSUPPORTED EXPERIENCE

Unsupported behavior is a feature, not an error.

If the backend returns:

> I couldn't find enough evidence of that in the supplied episodes, so I don't want to invent an answer.

Render it as a trustworthy response.

For example:

```text
I couldn't find this in the collection.

I searched the supplied episodes but couldn't find
enough evidence to answer this reliably. I don't want
to fill the gap with information from outside the collection.

Related material
...
```

Do not display:

- 404;
- "No results";
- stack traces;
- generic error UI.

Do not claim external search occurred unless it actually did.

---

# 20. EMPTY STATE

The first screen should quickly communicate what the product is.

Something like:

```text
FERMI COMPANION

Explore the ideas behind landmark scientific papers.

Ask a question about the episodes,
understand a difficult concept,
then trace the answer back to the audio.

[ What do you want to understand? ]

Try:
"Explain special relativity simply"
"Which episodes discuss information?"
"Compare Einstein and Bell"
```

Keep it concise.

The user should reach the conversation quickly.

---

# 21. RESPONSIVE DESIGN

Desktop is the primary target.

The experience should still work on mobile:

- conversation remains readable;
- input stays accessible;
- sources remain usable;
- audio controls remain usable;
- Explore can collapse into navigation;
- no horizontal overflow.

Do not spend excessive time on device-specific polish.

---

# 22. LOADING STATES

Use meaningful but truthful loading states.

Examples:

> Finding the relevant part of the collection...

> Building the explanation...

> Checking the source...

BUT:

Do not say "Checking the source" if the backend does not actually perform a source/grounding verification step.

Loading text must reflect actual system behavior.

Avoid blank screens and giant spinners.

---

# 23. ERROR STATES

Errors should:

- explain the issue in user-friendly language;
- offer retry;
- preserve existing conversation where possible;
- avoid technical stack traces;
- not pretend the model answered successfully.

Example:

> Something went wrong while getting that explanation.

[Try again]

---

# 24. FRONTEND ARCHITECTURE

Before introducing a state-management library or large component hierarchy, inspect the actual application size.

Prefer simple architecture.

Likely conceptual components:

```text
App
├── Conversation
│   ├── MessageList
│   ├── UserMessage
│   ├── AssistantMessage
│   ├── SourceCard
│   ├── FollowUpActions
│   └── Composer
│
├── Explore
│   ├── EpisodeSearch
│   ├── EpisodeList
│   └── EpisodeCard
│
└── AudioPlayer
```

This is illustrative.

Use component boundaries based on actual complexity.

Do not create abstractions merely because they look architecturally impressive.

---

# 25. API CLIENT

Create a small frontend API layer.

Do not scatter raw `fetch()` calls throughout UI components.

Conceptually:

```text
api/
  chat()
  getEpisodes()
  getEpisodeAudio()
```

But inspect the chosen frontend stack and use its existing conventions if appropriate.

The API layer should own:

- base URL;
- request construction;
- response parsing;
- API errors.

The UI should not know backend implementation details.

---

# 26. SESSION HANDLING

The backend uses `session_id`.

The frontend should:

1. create a session ID for a new conversation;
2. keep it stable during that conversation;
3. send it with each `/chat` request;
4. create a new session when the user selects "New conversation."

Do not assume backend persistence beyond its actual implementation.

If session state is in-memory, document that limitation.

---

# 27. SECURITY / FILE ACCESS

Do not expose:

- `.env`;
- API keys;
- arbitrary filesystem paths;
- internal data files unnecessarily;
- private backend artifacts.

If audio is served, use episode IDs or another controlled identifier.

Validate requested episode IDs.

---

# 28. INSPECT AND IMPROVE EXISTING TECHNIQUES

This is a key instruction.

Do not assume the previous implementation is optimal.

Inspect the actual code for:

- duplicated logic;
- unnecessary transformations;
- redundant API calls;
- inefficient serialization;
- duplicated metadata;
- brittle parsing;
- unnecessary dependencies;
- poor state handling;
- unnecessary backend/frontend coupling;
- opportunities to reuse existing evidence structures.

If you identify a better technique:

1. explain the current approach;
2. explain the proposed alternative;
3. explain why it is better;
4. estimate risk;
5. implement it only if it is clearly beneficial and within the two-day scope.

Do NOT perform broad refactors just because you prefer another coding style.

The goal is:

> improve the system where evidence justifies it.

Not:

> rewrite the system because another architecture looks cleaner.

---

# 29. DEVELOPMENT SEQUENCE

Follow this sequence.

## Stage 0 — Cross-IDE verification

Before coding:

- read project docs;
- inspect backend;
- inspect data;
- inspect CLI;
- inspect tests;
- inspect configuration;
- verify current routes;
- verify current response structures.

Produce a concise state report.

Do not modify code yet.

## Stage 1 — Backend/frontend contract

Implement only the minimum required contract improvements:

- structured sources;
- episode catalogue endpoint;
- controlled audio access;
- CORS/static serving if actually required.

But only after confirming these are genuinely necessary.

Run real API tests.

## Stage 2 — Frontend skeleton

Build:

- application shell;
- navigation;
- conversation route/screen;
- empty state;
- basic responsive structure.

Do not polish heavily yet.

## Stage 3 — Core conversation

Implement:

```text
question
 ↓
real /chat
 ↓
answer
 ↓
structured sources
```

No mocks in the final path.

## Stage 4 — Source verification

Implement:

- source cards;
- timestamps;
- excerpts;
- audio;
- jump-to-source.

Test against real podcast evidence.

## Stage 5 — Follow-up experience

Implement contextual conversation.

Test:

> Explain X.

followed by:

> I still don't understand that.

and:

> Explain it more simply.

## Stage 6 — Explore

Implement the actual episode catalogue.

## Stage 7 — Comparison

Render real comparison responses.

## Stage 8 — Unsupported behavior

Render actual unsupported responses.

## Stage 9 — Polish

Only after the complete product works:

- typography;
- spacing;
- animations;
- transitions;
- responsive details;
- empty/loading/error states.

---

# 30. VERIFICATION CHECKLIST

Before saying the frontend is complete, manually test:

### Conversation

1. Direct factual question
2. Conceptual explanation
3. Follow-up question
4. "Explain more simply"
5. Multi-turn context

### Sources

6. Source card appears
7. Episode name is correct
8. Timestamp is correct
9. Excerpt is correct if provided
10. Audio opens/plays
11. Audio jumps to source timestamp

### Discovery

12. Explore opens
13. Episode catalogue loads
14. Search/discovery works if supported
15. Metadata matches backend

### Comparison

16. Multi-episode comparison renders correctly
17. Per-episode sources remain distinguishable

### Unsupported

18. Unsupported request displays as intentional refusal

### Failure handling

19. Backend error
20. Audio error
21. Empty response / malformed response if relevant

Do not claim a behavior works until it has actually been exercised.

---

# 31. PERFORMANCE

Inspect actual performance before optimizing.

Potential areas to watch:

- unnecessary full episode catalogue fetches;
- repeated API requests;
- rendering extremely long messages;
- audio loading;
- conversation history growth;
- duplicate source rendering.

Do not prematurely optimize.

If the current backend has expensive operations, the frontend should avoid accidentally triggering them repeatedly.

For example:

A follow-up button should result in one intentional `/chat` request, not multiple duplicate requests.

---

# 32. ACCESSIBILITY

At minimum:

- keyboard-accessible composer;
- visible focus states;
- accessible buttons;
- semantic labels;
- readable contrast;
- audio controls accessible;
- source cards usable without relying solely on color.

Do not let visual polish reduce usability.

---

# 33. NO FAKE FEATURES

This is critical.

Do not create UI for functionality that does not exist.

Examples:

Do NOT show:

> Grounding score: 94%

unless the backend actually calculates this.

Do NOT show:

> 16 sources analyzed

unless the backend actually returns such information.

Do NOT show:

> Confidence: High

unless confidence is actually calculated.

Do NOT show:

> AI verified this answer

unless an actual verification mechanism exists.

The UI must reflect reality.

---

# 34. PROJECT CONTINUITY

At the end of every meaningful session:

Update `STATUS.md` with:

```text
Current phase
Completed
In progress
Verified
Not verified
Known issues
Files changed
Tests/checks run
Next task
```

Update `DECISIONS.md` when an architecture/product decision changes.

Never rely on chat history.

A future agent should be able to open the repository and understand the project.

---

# 35. FIRST TASK — DO NOT CODE YET

Your first response in this new IDE must NOT implement the frontend.

Instead:

## A. Read all project documentation.

## B. Inspect the actual repository.

## C. Inspect:

- backend;
- API routes;
- models;
- retrieval;
- evidence;
- manifest;
- audio mapping;
- CLI;
- tests;
- configuration;
- generated data;
- current package/dependency setup.

## D. Verify the previous agent's frontend integration report.

Specifically verify whether these statements are true:

1. There is no frontend.
2. `/chat` only returns a markdown response + intent.
3. Sources are embedded in markdown.
4. Audio is not currently exposed through HTTP.
5. The episode manifest is not currently exposed as an API.
6. Session state is in-memory.
7. Discovery is currently handled through the existing backend intent.
8. Comparison is handled through the existing backend intent.
9. Unsupported behavior is already implemented.

Do not assume any of these are true.

## E. Inspect the existing implementation for better alternatives.

For each proposed change:

```text
Current implementation:
...

Problem:
...

Simplest frontend requirement:
...

Existing reusable mechanism:
...

Recommended change:
...

Why:
...
```

## F. Produce a final cross-IDE technical assessment containing:

1. Actual project state
2. Backend architecture
3. Current evidence flow
4. Current source/provenance representation
5. Current audio representation
6. Current manifest/catalogue representation
7. Current conversation/session architecture
8. Frontend integration gaps
9. Which backend changes are genuinely required
10. Which proposed changes can be avoided/replaced with better existing mechanisms
11. Recommended frontend architecture
12. Recommended component structure
13. Recommended API contract
14. Risks
15. What should be implemented first

Then STOP.

Do not write application code until this assessment is complete.

The purpose of this first step is to ensure that you are continuing the existing project rather than accidentally creating a second architecture on top of it.