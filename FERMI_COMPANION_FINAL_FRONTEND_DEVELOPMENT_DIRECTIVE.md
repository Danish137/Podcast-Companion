# FERMI COMPANION — FINAL FRONTEND DEVELOPMENT DIRECTIVE

## Purpose

You are taking over an existing AI engineering project from another coding environment.

This is **not a greenfield project**.

The backend, ingestion, transcription, retrieval, conversation logic, and evaluation system already exist. The frontend is now being built on top of that system.

This document is the final product and engineering direction for the frontend phase.

**Do not create another validation/review checkpoint after reading this document.** The decisions and corrections below are already incorporated. Inspect the existing code as part of implementation, make necessary compatibility adjustments, and proceed directly with the build.

You may improve implementation techniques when inspection clearly reveals a simpler, safer, or more maintainable approach, but do not change the product direction defined here.

---

# 1. PROJECT CONTEXT

The product is:

## Fermi Companion

A grounded AI learning companion for understanding landmark scientific ideas discussed in the supplied Fermi Podcast collection.

The product is **not**:

- a generic RAG chatbot;
- a transcript search engine;
- a podcast browser;
- an episode catalogue;
- an episode-specific chatbot;
- a dashboard of podcast episodes.

The central learner loop is:

**ASK → UNDERSTAND → VERIFY → EXPLORE**

The learner should be able to:

- ask natural-language questions;
- understand difficult scientific concepts;
- ask contextual follow-ups;
- ask for simpler/deeper explanations;
- compare ideas;
- discover relevant material;
- verify answers against the original supplied audio;
- listen from the relevant source timestamp;
- understand when the supplied collection does not contain enough evidence.

The frontend should make this product identity obvious.

---

# 2. READ PROJECT CONTEXT AND INSPECT THE REAL CODEBASE

Before implementing, read:

1. `AGENTS.md`
2. `STATUS.md`
3. `DECISIONS.md`
4. `PROJECT_SPEC.md`
5. `PRODUCT.md`
6. `ARCHITECTURE.md`
7. `EVALUATION.md`
8. `IMPLEMENTATION_PLAN.md`
9. `DEVELOPMENT_PROTOCOL.md`

Then inspect the actual repository, including:

- complete backend implementation;
- FastAPI routes;
- retrieval/evidence implementation;
- conversation/session implementation;
- episode manifest;
- transcript/chunk structures;
- audio file mapping;
- CLI;
- tests;
- configuration;
- dependencies;
- generated artifacts.

The existing code is authoritative for implementation details.

If documentation and implementation differ, inspect the implementation and make the smallest compatibility adjustment necessary. Update `STATUS.md` if the project state has materially changed.

Do not rewrite working systems simply because another architecture is stylistically preferable.

---

# 3. PRODUCT DIRECTION — NO EPISODE-BROWSING UI

This is a critical product decision.

The existence of an episode manifest does **not** mean the learner should browse or select episodes.

Do NOT build:

- an episode catalogue page;
- a grid/list of all episodes;
- episode cards as primary navigation;
- an episode selector;
- an episode dropdown;
- a “current episode” mode;
- “select an episode to chat”;
- episode-specific chat;
- persistent episode navigation/sidebar;
- episode filters whose purpose is to constrain the conversation to one episode;
- a UI that asks the learner to choose an episode before asking a question.

The learner should interact with the companion across the entire supplied collection.

The companion should identify relevant episodes/material automatically based on the learner's question.

## Discovery is conversational

For example:

**User:**  
“What in this collection would help me understand information theory?”

The companion can answer conversationally with relevant material.

**User:**  
“What should I explore if I'm interested in the history of computing?”

The companion can recommend relevant material.

**User:**  
“Compare Shannon's work with the later transformer paper.”

The companion should automatically identify and compare the relevant material.

The learner should never have to browse a catalogue to accomplish these tasks.

---

# 4. EPISODE METADATA VS PRODUCT NAVIGATION

Episode metadata remains useful in the backend.

It can support:

- retrieval;
- conversational discovery;
- comparison;
- source provenance;
- audio mapping.

But:

**EPISODE METADATA = backend knowledge/provenance**

NOT:

**EPISODE METADATA = primary frontend navigation**

Episode information may appear in the UI only when useful as:

1. source provenance;
2. a timestamped audio verification target;
3. conversational recommendation/discovery;
4. comparison context.

For example:

```text
SOURCE

Great Papers 04
Shannon and the Birth of Information

18:32 – 19:17

[relevant excerpt]

▶ Listen from 18:32
```

This is source verification, not episode browsing.

---

# 5. INFORMATION ARCHITECTURE

The primary UI is conversation-first.

Conceptually:

```text
                         FERMI COMPANION
                               |
                               v
                         CONVERSATION
                               |
                    +----------+----------+
                    |          |          |
                    v          v          v
                 Explain    Compare   Discover
                    |          |          |
                    +----------+----------+
                               |
                               v
                         GROUNDED ANSWER
                               |
                               v
                            SOURCES
                               |
                        Episode + timestamp
                               |
                               v
                             AUDIO
```

There should NOT be a primary navigation branch for an episode catalogue.

The collection is the companion's knowledge base, not the product's navigation hierarchy.

---

# 6. INITIAL EXPERIENCE

The initial screen should be simple and conversational.

Conceptually:

```text
FERMI COMPANION

Explore the ideas behind landmark scientific papers.

Ask a question about the collection,
understand a difficult concept,
then trace the answer back to the audio.

[ What do you want to understand? ]

Try:

“Explain special relativity simply”

“Which material covers information theory?”

“Compare Einstein and Bell”

“Does the collection discuss string theory?”
```

Keep the empty state concise.

The learner should reach the conversation immediately.

---

# 7. CONVERSATION EXPERIENCE

The conversation is the most important UI.

Support:

- user messages;
- assistant messages;
- readable markdown;
- mathematical notation where necessary;
- loading state;
- error state;
- contextual follow-ups;
- source evidence;
- audio verification.

Example:

```text
USER

Why did Einstein need special relativity?


COMPANION

[clear explanation]


SOURCE

Great Papers 01
18:42 – 19:31

[excerpt]

▶ Listen from 18:42
```

Useful contextual actions may include:

- Explain this more simply
- Give me an analogy
- Go deeper
- What should I understand next?

Only show contextual actions when useful.

Do not create a permanent wall of buttons.

---

# 8. SOURCE VERIFICATION IS A CORE PRODUCT FEATURE

Source evidence is not a citation footer.

It should communicate:

1. what episode supports the answer;
2. where in the episode;
3. relevant excerpt if available;
4. ability to listen from that point.

Preferred presentation:

```text
SOURCE

Great Papers 01
Einstein's Special Relativity

18:42 – 19:31

[relevant excerpt]

▶ Listen from 18:42
```

Do **not** expose retrieval similarity scores to the learner.

Do not show:

- “Similarity: 0.87”;
- vector-search scores;
- embedding details;
- internal retrieval metadata.

Those may remain internal for engineering/evaluation.

The learner needs evidence and provenance, not vector-search internals.

---

# 9. STRUCTURED SOURCE CONTRACT

The previous implementation assessment identified that the backend currently embeds source citations into markdown, for example:

`[Episode Title, MM:SS]`

Do **not** make the frontend parse those citations with regex.

Inspect the actual retrieval/evidence implementation.

If, as expected, the backend already has richer evidence objects containing information such as:

- episode ID;
- episode title;
- start time;
- end time;
- text;

then expose that existing evidence through a structured `sources` field in the chat response.

Conceptually:

```json
{
  "response": "...",
  "intent_used": "...",
  "sources": [
    {
      "episode_id": "...",
      "episode_title": "...",
      "start_time": 1122,
      "end_time": 1178,
      "excerpt": "..."
    }
  ]
}
```

This is conceptual only.

Use the actual evidence structures already present.

Do not create a second retrieval mechanism or duplicate evidence model unnecessarily.

Rules:

- Never fabricate timestamps.
- Never fabricate excerpts.
- Never fabricate episode IDs.
- Never fabricate source relationships.
- Reuse the evidence actually used by the backend.
- Preserve provenance.
- If a field is unavailable, make it optional rather than inventing it.

The frontend must display evidence from the same retrieval path used to generate the answer.

The flow must remain:

```text
User
  ↓
/chat
  ↓
existing intent/retrieval
  ↓
existing evidence
  ↓
LLM
  ↓
answer + structured evidence
  ↓
frontend
```

There must not be an independent frontend retrieval system.

---

# 10. EPISODE MANIFEST / METADATA

The backend already uses an episode manifest.

It may contain:

- episode metadata;
- paper title;
- authors;
- year;
- field;
- concepts;
- summary;
- audio mapping.

This is useful internally and for conversational discovery.

If the frontend genuinely needs canonical metadata, expose it through a small endpoint such as:

`GET /episodes`

But do not automatically turn that endpoint into an episode catalogue UI.

Do not:

- hardcode metadata in React;
- create a second manifest;
- expose all episodes as a browse screen.

Use metadata only when needed for:

- source presentation;
- conversational recommendations;
- comparisons;
- audio mapping;
- relevant UI behavior.

---

# 11. METADATA VS AUDIO-GROUNDED EVIDENCE

Keep these layers distinct.

## Catalogue metadata

Examples:

- author;
- year;
- field;
- paper title;
- concepts;
- summary.

These may come from the existing manifest.

## Podcast-grounded evidence

This comes from:

```text
supplied raw audio
→ our transcription
→ timestamped transcript
→ retrieval evidence
```

The existence of catalogue metadata does not mean the podcast itself said that fact.

Do not silently present catalogue metadata as something the podcast established.

For conversational answers requiring source evidence, use podcast-grounded evidence.

---

# 12. AUDIO ACCESS

Verify whether the backend currently exposes podcast audio over HTTP.

If it does not, add the smallest clean mechanism required for source verification.

Prefer a controlled route such as:

`GET /episodes/{episode_id}/audio`

or another equivalent approach if inspection reveals a better existing mechanism.

Requirements:

- use canonical episode ID → audio mapping;
- reject unknown episode IDs;
- never accept arbitrary filesystem paths;
- do not expose the entire filesystem;
- return the correct audio content type;
- preserve browser HTTP range/seek behavior where possible.

Do NOT build:

- HLS;
- DASH;
- custom streaming infrastructure;
- cloud media infrastructure;
- unnecessary media architecture.

The requirement is simply:

**Listen from the source timestamp.**

---

# 13. AUDIO PLAYER UX

Keep it compact.

This is not a podcast-player product.

The important interaction is:

**▶ Listen from 18:42**

When clicked:

- load the correct supplied audio;
- seek to the source timestamp;
- allow normal playback;
- show basic playback position where useful.

Do not build an elaborate podcast interface.

---

# 14. COMPARISON EXPERIENCE

Comparison is one of the strongest ways to differentiate the product from generic RAG.

When the backend returns a multi-episode comparison, visually communicate the structure.

Conceptually:

```text
How these ideas differ

Einstein
────────────
[explanation]

Source
18:42 – 19:31


Bell
────────────
[explanation]

Source
22:14 – 23:02


The connection
────────────
[synthesis]
```

The learner should not have selected Einstein or Bell from the UI.

The system identified them because the question required them.

Preserve per-episode provenance.

---

# 15. UNSUPPORTED QUESTIONS

Unsupported behavior is a product feature.

If the collection does not contain enough evidence:

> I couldn't find enough evidence of that in the supplied episodes, so I don't want to invent an answer.

Render this as a trustworthy response, not an error.

Do not display:

- 404;
- “No results”;
- technical failure;
- generic error UI.

Do not supplement with general model knowledge and present it as podcast-grounded information.

---

# 16. VISUAL DESIGN

The interface should feel:

- intelligent;
- calm;
- scientific;
- editorial;
- focused;
- modern;
- trustworthy.

Prioritize:

- excellent typography;
- whitespace;
- hierarchy;
- readability;
- restrained color;
- subtle interactions.

Avoid generic AI SaaS aesthetics:

- excessive gradients;
- glowing AI effects;
- giant hero graphics;
- excessive rounded cards;
- dashboard metric panels;
- AI sparkle decoration;
- unnecessary animations.

The UI should feel like a serious learning product.

---

# 17. CONVERSATION SHOULD DOMINATE

Do not permanently place a large episode list beside the conversation.

The user should not feel like they are browsing a podcast library.

Preferred structure:

```text
┌────────────────────────────────────────────────────────┐
│ Fermi Companion                              Explore   │
├────────────────────────────────────────────────────────┤
│                                                        │
│                  Conversation                          │
│                                                        │
│              User question                             │
│                                                        │
│              Companion answer                          │
│                                                        │
│              Source evidence                            │
│                                                        │
│              Follow-up                                  │
│                                                        │
│              [ Ask a follow-up... ]                     │
│                                                        │
└────────────────────────────────────────────────────────┘
```

“Explore” here means conversational discovery or another lightweight secondary surface.

It does NOT mean episode browsing.

---

# 18. DO NOT BUILD FEATURES JUST BECAUSE THE BACKEND HAS THEM

The UI should be driven by learner intent, not database structure.

For every proposed feature ask:

1. Does the learner need this?
2. Does the assignment require this?
3. Does it improve ASK → UNDERSTAND → VERIFY → EXPLORE?
4. Does it make the product more useful?
5. Does it risk turning the product into a podcast browser?

If not, do not add it.

---

# 19. BACKEND MODIFICATION PRINCIPLE

The backend is functionally complete for the trial scope.

Do not rewrite:

- retrieval;
- transcription;
- prompts;
- intent logic;
- evaluation;
- conversation architecture;

unless a concrete frontend integration blocker requires it.

Preferred backend additions are small and additive:

1. structured sources in `/chat`;
2. canonical episode metadata access if genuinely needed;
3. controlled audio access;
4. CORS only if genuinely needed.

However, inspect the implementation first.

If an existing mechanism already solves one of these, reuse it.

---

# 20. ENGINEERING REVIEW DURING IMPLEMENTATION

You are authorized to improve our proposed technical approach when inspection of the existing code clearly reveals a better solution.

Before a meaningful architectural change, determine:

```text
CURRENT IMPLEMENTATION:
...

PROBLEM:
...

EXISTING REUSABLE MECHANISM:
...

PROPOSED CHANGE:
...

WHY IT IS BETTER:
...

RISKS:
...
```

Do not perform broad refactors just because you prefer another coding style.

The goal is the smallest reliable change that improves the product.

---

# 21. FRONTEND API CLIENT

Keep frontend API calls centralized.

Prefer a small API layer such as:

- `chat()`
- `getEpisodes()` only if genuinely needed
- `getEpisodeAudio()`

Do not scatter raw fetch calls throughout components.

Use the existing frontend stack if one already exists.

If no frontend exists, choose a lightweight, maintainable stack appropriate for the project.

Do not introduce heavy state management without a real need.

---

# 22. SESSION MANAGEMENT

The backend currently uses `session_id`.

Verify the implementation.

The frontend should:

- create a new session ID for a new conversation;
- keep it stable within that conversation;
- send it with every `/chat`;
- create a new session when the user starts a new conversation.

Do not claim persistence across backend restarts if the backend uses in-memory state.

---

# 23. RESPONSIVE DESIGN

Desktop is primary.

Mobile should remain usable.

Ensure:

- readable conversation;
- accessible composer;
- usable source cards;
- usable audio controls;
- no horizontal overflow;
- secondary navigation can collapse.

Do not spend disproportionate time on device-specific polish.

---

# 24. ACCESSIBILITY

At minimum:

- keyboard-accessible input;
- accessible buttons;
- visible focus states;
- semantic labels;
- readable contrast;
- usable audio controls.

---

# 25. LOADING STATES

Loading states must describe actual behavior.

Examples:

- “Finding relevant material...”
- “Preparing the explanation...”
- “Retrieving supporting evidence...”

Only use wording that corresponds reasonably to actual backend behavior.

Do not falsely claim a verification step is occurring if none exists.

---

# 26. ERROR STATES

User-facing errors should:

- be understandable;
- provide retry;
- avoid stack traces;
- preserve the conversation where possible.

Do not hide genuine backend failures by rendering a fake assistant answer.

---

# 27. NO FAKE FEATURES

Never render information the backend does not actually provide.

Do NOT invent:

- confidence percentages;
- grounding scores;
- retrieval scores;
- source counts;
- verification badges;
- episode metadata;
- timestamps;
- excerpts;
- “AI verified” labels.

The frontend must reflect reality.

---

# 28. PERFORMANCE

Inspect actual behavior before optimizing.

Avoid:

- duplicate `/chat` calls;
- repeated expensive API requests;
- unnecessarily loading the full corpus;
- unnecessarily loading audio before the user requests it;
- rendering unnecessarily large hidden DOM structures.

Do not prematurely optimize.

---

# 29. CORPUS CONTEXT

The assignment brief describes:

3 raw audio files, <=3 hours.

The actual supplied corpus contains:

16 episodes, approximately 9.6 hours.

Do not silently redefine the assignment as “16 episodes required.”

The backend currently supports the supplied collection.

The frontend should remain corpus-size agnostic.

Do not hardcode “16 episodes” into the product UI.

The user should not see a “16 episode library” presentation.

The collection should simply feel like the companion's knowledge base.

---

# 30. EVALUATION CONTEXT

The backend already has an evaluation system.

Do not break it.

Current evaluation results must not be presented as proof of general correctness.

“10/10 passing” means the selected evaluation cases passed.

It does not mean:

- perfect accuracy;
- production-ready;
- no hallucinations;
- universally correct.

Do not expose evaluation internals to normal users.

When describing the backend, use:

**“functionally complete for the trial scope”**

rather than:

**“production-ready.”**

---

# 31. DEVELOPMENT SEQUENCE

Unlike an assessment/handoff phase, this directive does NOT require another validation checkpoint.

You have already received and incorporated the product corrections.

Proceed directly with implementation after inspecting the codebase.

## Phase 0 — Verify while implementing

Read the docs and inspect the actual code.

Do not stop to ask for another validation round.

Resolve minor documentation/code discrepancies using engineering judgment and record material changes in `STATUS.md`.

## Phase 1 — API contract

Implement only genuinely required backend integration changes:

- structured `/chat` sources;
- controlled audio endpoint;
- metadata endpoint only if genuinely needed;
- CORS only if genuinely needed.

Verify these with real requests.

## Phase 2 — Frontend shell

Build:

- application shell;
- conversation screen;
- empty state;
- navigation;
- responsive structure.

Do NOT build an episode catalogue.

## Phase 3 — Core conversation

Implement:

```text
question
→ real /chat
→ answer
→ structured sources
```

No fake data in the final path.

## Phase 4 — Source verification

Implement:

- source cards;
- timestamp;
- excerpt;
- audio;
- seek-to-source.

## Phase 5 — Follow-up learning

Implement contextual follow-ups.

Test:

> Explain X.

then:

> I still don't understand.

then:

> Explain it more simply.

## Phase 6 — Conversational discovery

Support questions such as:

> Which material covers information theory?

> What should I explore if I want to understand computation?

Do this through conversation.

Do NOT create an episode browser.

## Phase 7 — Comparison

Render actual comparison responses with per-source provenance.

## Phase 8 — Unsupported behavior

Render actual unsupported responses intentionally.

## Phase 9 — Polish

Only after the complete product works:

- typography;
- spacing;
- visual hierarchy;
- transitions;
- responsive details;
- accessibility;
- loading/error states.

---

# 32. VERIFICATION CHECKLIST

Before declaring the frontend complete, test with real backend data.

## Conversation

1. factual question;
2. conceptual explanation;
3. follow-up;
4. “explain more simply”;
5. multi-turn context.

## Sources

6. source appears;
7. episode name correct;
8. timestamp correct;
9. excerpt correct if available;
10. audio works;
11. audio seeks to source.

## Discovery

12. conversational discovery query;
13. relevant material mentioned naturally;
14. no episode-selection UI required.

## Comparison

15. multi-episode comparison;
16. per-source provenance.

## Unsupported

17. unsupported request;
18. trustworthy refusal.

## Errors

19. backend error;
20. audio error.

Do not claim a behavior works unless it has actually been tested.

---

# 33. PROJECT MEMORY / CROSS-IDE CONTINUITY

At the end of every meaningful development phase update `STATUS.md`.

Include:

- current phase;
- completed;
- in progress;
- verified;
- not verified;
- known issues;
- files changed;
- tests/checks run;
- next task.

Update `DECISIONS.md` when architecture/product decisions change.

Do not rely on chat history.

Another coding agent should be able to continue from the repository alone.

---

# 34. FINAL IMPLEMENTATION OUTCOME

The final product should feel like:

> **An intelligent companion that helps me understand a body of scientific ideas and lets me verify what it tells me.**

It should NOT feel like:

> **A chatbot sitting on top of a podcast episode browser.**

The 16 supplied episodes are the knowledge collection.

They are not the primary navigation structure of the product.

The learner's primary interaction is always:

**ASK → UNDERSTAND → VERIFY → EXPLORE**

Proceed with implementation.
