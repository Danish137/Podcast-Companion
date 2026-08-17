# Architecture and Product Decision Log

This file records decisions that affect product behavior, architecture, scope, evaluation, or trust.

Do not rewrite history. Add new decisions.

## Decision format

For each decision:

- Date
- Decision
- Context
- Options considered
- Choice
- Why
- Consequences
- Revisit condition

---

## D001 - Product is a learning companion, not a transcript chatbot

Date: 2026-08-15

Decision:

The primary product is a conversational study companion for learning physics from the supplied podcast collection.

Why:

The assignment asks the candidate to define a valuable learner problem and explicitly says the experience should do more than display a transcript or one-time summary.

Consequences:

Architecture must support tutoring, follow-ups, discovery, comparison, and source verification.

---

## D002 - Podcast audio is the source of truth

Date: 2026-08-15

Decision:

Substantive factual answers about the collection must be grounded in supplied podcast evidence.

Why:

Trustworthiness and source verifiability are central evaluation criteria.

Consequences:

Transcription, timestamps, provenance, retrieval, and grounding checks are first-class.

---

## D003 - Support arbitrary episode count

Date: 2026-08-15

Decision:

The ingestion pipeline accepts an arbitrary number of audio files.

Why:

The assignment brief describes 3 files, while the candidate reports receiving 15-16 files of approximately 30 minutes each. The architecture should not hardcode the assignment example.

Consequences:

Episode discovery and indexing must be collection-based rather than assuming a fixed count.

---

## D004 - Do not add sophisticated architecture without evidence

Date: 2026-08-15

Decision:

Avoid agent swarms, knowledge graphs, fine-tuning, or other complex mechanisms unless an observed product/evaluation failure justifies them.

Why:

The trial is timeboxed to two days and evaluates judgment and complete execution.

Consequences:

Prefer simple, testable components.

---

## D005 - Transcription via Gemini 2.5 Flash audio input

Date: 2026-08-16

Decision:

Use Gemini 2.5 Flash via OpenRouter for transcription. The model natively accepts audio input and can produce timestamped transcripts.

Options considered:

1. OpenAI Whisper API — not available on OpenRouter; would require separate OpenAI key
2. Local whisper / faster-whisper — requires GPU or slow CPU inference for 9.6 hours; not installed
3. Gemini 2.5 Flash audio input via OpenRouter — already available, very cheap ($0.000001/token audio), natively supports audio

Choice: Option 3

Why:

- Single API provider (OpenRouter) for both transcription and chat
- Native audio understanding, not just ASR — can produce structured output
- Very cost-effective for 9.6 hours of audio
- No local GPU dependency

Consequences:

- Audio must be split into segments (API has input limits)
- Timestamps are approximate (based on audio segment offsets + model output), not word-level
- Must verify transcript quality against actual audio on a sample
- If quality is insufficient, revisit with local whisper

Revisit condition: If transcript quality is materially poor on sample verification.

---

## D006 - ChromaDB for local vector store with Gemini embeddings

Date: 2026-08-16

Decision:

Use ChromaDB as the local vector store. Use Gemini 2.5 Flash to generate embedding-friendly text representations since OpenRouter does not offer embedding models.

Options considered:

1. OpenAI embeddings — requires separate API key not provided
2. Sentence-transformers local — requires additional large dependency, potential GPU issues
3. ChromaDB default embeddings (all-MiniLM-L6-v2) — lightweight, local, no API needed
4. Gemini for generating search-friendly representations + ChromaDB default embeddings

Choice: Option 3/4 hybrid — use ChromaDB's built-in embedding function (uses all-MiniLM-L6-v2 internally) for initial baseline. If retrieval quality is poor, switch to Gemini-generated representations.

Why:

- No additional API calls for embedding (saves budget)
- ChromaDB handles embedding internally with a decent default model
- Simple to set up and evaluate
- Can upgrade embedding approach as the "meaningful improvement" if baseline retrieval fails

Consequences:

- Embedding quality limited to all-MiniLM-L6-v2 (384-dim)
- May not capture scientific terminology as well as larger models
- Easy to swap later

Revisit condition: If baseline evaluation shows retrieval failures traceable to embedding quality.

---

## D007 - Product framing is interdisciplinary, not physics-only

Date: 2026-08-16

Decision:

The product is framed as a learning companion for "landmark scientific papers" across disciplines, not physics only.

Why:

The actual supplied corpus ("Great Papers" series) includes biology (DNA), information theory (Shannon), computer science (Turing), mathematics (Gödel), game theory (Nash), chemistry (Mendeleev), and evolution (Darwin) alongside physics episodes.

Consequences:

Product documentation, system prompts, and metadata must not assume physics-only content. Discovery should support filtering by discipline/field.

---

## D008 - Bypass semantic retrieval for DISCOVER intent

Date: 2026-08-16

Decision:

For queries classified as `DISCOVER` (e.g. finding episodes by topic/field), bypass ChromaDB entirely and inject the full `episode_manifest.json` into the LLM context.

Context:

Semantic search on 90-second chunks often fails to effectively answer high-level catalogue queries ("Which episodes are about biology?").

Choice:

Inject global metadata.

Why:

The manifest is small enough (~20KB) to fit comfortably in the LLM context window. This provides 100% accurate grounded discovery without hallucinations or relying on semantic similarity of arbitrary text chunks.

Consequences:

Discovery questions scale directly with the size of the metadata manifest. If the catalogue grows too large, the manifest will no longer fit in context, requiring a different approach.

Revisit condition: If the catalogue size exceeds the LLM context limits or budget constraints.

