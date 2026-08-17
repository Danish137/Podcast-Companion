# Project Status

> This file is the current operational memory of the project.
> Update it at the end of every meaningful work session.

## Current phase

`PHASE_9 - FRONTEND IMPLEMENTATION`

## Overall status

Phase 8 (Demo and Documentation) completed. Backend API extended with structured sources and audio endpoints. Frontend initialization in progress.

## Product goal

Build Fermi Companion, a grounded conversational learning companion over the supplied Fermi Podcast audio.

See `PRODUCT.md`.

## Current capabilities

None yet.

## Completed

- [x] Repository initialized
- [x] Audio inventory completed
- [x] Transcription pipeline working
- [x] Timestamped transcript artifacts generated
- [x] Episode metadata generated
- [x] Retrieval working
- [x] Minimal end-to-end chat working
- [x] Source/timestamp evidence working
- [x] Unsupported handling working
- [x] Episode discovery working
- [x] Cross-episode comparison working
- [x] Evaluation set created
- [x] Baseline evaluation run (on ep01 vertical slice)
- [x] Manual failure analysis completed
- [x] Meaningful improvement implemented
- [x] Improved evaluation rerun
- [x] Backend API extended with structured sources
- [x] Audio serving endpoint added
- [x] CORS configured for frontend development
- [x] Frontend project initialized (React 19 + TypeScript + Vite)
- [x] Tailwind CSS configured
- [x] API client and types created
- [ ] Frontend UI components
- [ ] README complete
- [ ] PRODUCT.md complete
- [ ] EVAL.md complete
- [ ] Demo complete

## Actual corpus

Assignment brief states: 3 raw audio files, ≤3 hours total.

Project docs note: candidate workspace may contain 15-16 files of ~30 minutes each.

**Verified inventory (2026-08-16, Session 2):**

Series: **"Great Papers"** — interdisciplinary (physics, CS, biology, math, information theory, game theory)

| # | Episode | Duration | Size |
|---|---------|----------|------|
| 01 | Einstein's Special Relativity | 52.2 min | 47.8 MB |
| 02 | How Black Holes Radiate, Hawking 1975 | 45.3 min | 41.5 MB |
| 03 | The Double Helix, Watson and Crick 1953 | 43.3 min | 39.6 MB |
| 04 | Shannon and the Birth of Information, 1948 | 39.9 min | 36.5 MB |
| 05 | Attention Is All You Need, 2017 | 36.4 min | 33.3 MB |
| 06 | General Relativity, Einstein 1915 | 33.8 min | 30.9 MB |
| 07 | On Computable Numbers, Turing 1936 | 33.0 min | 30.2 MB |
| 08 | Natural Selection, Darwin and Wallace 1858 | 33.2 min | 30.4 MB |
| 09 | Bell's Theorem, 1964 | 34.0 min | 31.1 MB |
| 10 | The Expanding Universe, Hubble 1929 | 32.9 min | 30.1 MB |
| 11 | The Birth of the Quantum, Planck 1900 | 33.1 min | 30.3 MB |
| 12 | The Dirac Equation and Antimatter, 1928 | 33.0 min | 30.2 MB |
| 13 | How DNA Copies Itself, Meselson-Stahl 1958 | 32.7 min | 29.9 MB |
| 14 | Gödel's Incompleteness Theorems, 1931 | 32.3 min | 29.6 MB |
| 15 | The Periodic Table, Mendeleev 1869 | 31.2 min | 28.6 MB |
| 16 | Nash Equilibrium and Game Theory, 1950 | 32.5 min | 29.8 MB |

**Total: 16 episodes, 578.8 minutes (9.6 hours), 529.9 MB, all MP3**

Note: Assignment brief says 3 files ≤ 3 hours. Actual corpus is 16 files / 9.6 hours. Discrepancy documented in DECISIONS.md D003. Pipeline is configurable for arbitrary episode count.

## Current Phase: Phase 9 (Frontend Implementation)

**Status:** UX/UI Redesign Complete

**Completed Work:**
- Backend API extended with `SourceEvidence` model
- POST `/chat` now returns structured `sources` array with episode metadata, timestamps, and excerpts
- GET `/episodes/{episode_id}/audio` endpoint added with HTTP range support for seeking
- CORS middleware configured for local development
- Frontend React project initialized with TypeScript and Vite
- Tailwind CSS v4 configured with Vite plugin
- react-markdown installed for markdown rendering
- TypeScript API types defined (`SourceEvidence`, `ChatResponse`, `Message`)
- API client created with typed `chat()` and `getAudioUrl()` functions
- Utility functions for timestamp formatting created
- **Complete UX/UI redesign implemented:**
  - Professional design system with Inter typography
  - Restrained color palette (neutral grays + blue accent)
  - Redesigned empty state with centered composition
  - Premium composer with integrated send button
  - Editorial typography for assistant responses
  - Polished source cards with subtle borders
  - Dark audio player with modern controls
  - Consistent spacing and visual hierarchy
  - No duplicate branding
  - Calm, scientific, editorial aesthetic

**Verified Working:**
- Real `/chat` API integration working
- Structured sources displaying correctly
- Audio player with timestamp seeking functional
- Session management maintaining context
- Loading and error states displaying properly
- Markdown rendering in responses
- Multi-source display with provenance

**Next Task:**
- Manual testing of all scenarios (discovery, comparison, unsupported)
- Cross-browser verification
- Mobile responsive testing
- Final STATUS.md update and documentation

## Current architecture

The repository contains documentation, a `src/` directory with Python source code for the ingestion and retrieval pipeline, and a `Podcast/` directory with 16 MP3 files.

Key files in `src/`:
- `transcribe.py`: Audio splitting and transcription via Gemini 2.5 Flash
- `chunker.py`: Text chunking with overlap
- `metadata.py`: Episode metadata extraction
- `retrieval.py`: ChromaDB vector store wrapper
- `companion.py`: Core chat and QA logic with intent routing
- `api.py`: FastAPI backend with `/chat` and `/episodes/{id}/audio` endpoints
- `cli.py`: Terminal interface for testing
- `evaluate.py`: Evaluation framework

Frontend structure in `frontend/`:
- `src/api/client.ts`: Centralized API calls
- `src/types/api.ts`: TypeScript interfaces
- `src/utils/format.ts`: Timestamp formatting utilities
- Components (in progress): Layout, Conversation, EmptyState, SourceCard, AudioPlayer
- `companion.py`: Core chat and QA logic
- `api.py` / `cli.py`: Interfaces
- `evaluate.py`: Evaluation script

## Current runtime environment

Verified available on the system:

| Tool          | Version              |
|---------------|----------------------|
| Python        | 3.14.0               |
| Node.js       | 24.12.0              |
| npm           | 11.6.2               |
| ffmpeg        | 8.1.2-essentials     |

Relevant Python packages already installed (global):

| Package                 | Version  |
|-------------------------|----------|
| openai                  | 2.40.0   |
| langchain               | 1.3.4    |
| langchain-openai        | 1.2.2    |
| langchain-community     | 0.4.2    |
| langchain-text-splitters | 1.1.2   |
| fastapi                 | 0.135.3  |
| uvicorn                 | 0.43.0   |
| httpx                   | 0.28.1   |
| tiktoken                | 0.13.0   |
| numpy                   | 2.4.2    |
| scipy                   | 1.17.1   |
| pydantic                | 2.12.5   |

Notable **missing** packages (will need installation for Phase 1+):
- Vector DB (chromadb) will be needed unless already available in environment.

## Current model/provider setup

OpenRouter API access is expected per assignment.

Exact model selection: `Gemini 3.1 Pro (Low)`

## Last completed work

Phase 7 completed. Meaningful improvement (episode manifest injection for DISCOVER intent) implemented and successfully verified against the eval set.

## Current blockers

None.

## Known unknowns

- Exact model budget constraints

## Last verification

Ran evaluation (`eval_improved_full_20260816_040944.json`) which showed 10/10 cases passed. Verified artifacts in `data/` and `eval/results/`.

## Next task

1. Complete `README.md`, `EVAL.md`, and `PRODUCT.md`.
2. Finalize Demo.


## Session log

### Session 0

Date: 2026-08-15

State: project context pack created.

Next action: run the bootstrap/audit prompt against the repository.

### Session 2

Date: 2026-08-16

State: Phase 1 (Ingestion) implemented. Audio files present.

Actions performed:
- Audio files (16 episodes, ~9.6 hours) found in `Podcast/`.
- Implemented `transcribe.py`, `chunker.py`, `metadata.py`, `retrieval.py` in `src/`.
- Implemented core companion (`companion.py`) and evaluation (`evaluate.py`).
- Updated `DECISIONS.md` (D005-D007).

Blockers:
- Need to configure API keys (`OPENROUTER_API_KEY`) and run the full ingestion pipeline.

Next action: Set up the environment (install dependencies like ChromaDB), configure API keys, and run the pipeline.

### Session 3 (Recovery)

Date: 2026-08-16

State: Phase 8 (Demo and documentation). Recovered state from transcript.

Actions performed:
- Reconciled transcript claims against physical repository.
- Verified 16 episodes fully ingested (transcripts, chunks, metadata, chromadb index).
- Verified `eval_improved_full` ran successfully with 10/10 cases passing.
- Updated STATUS.md to reflect actual current state.

Next action: Create EVAL.md and finalize documentation.

