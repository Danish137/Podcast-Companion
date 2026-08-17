# Fermi Podcast Companion

## What it is
The Fermi Podcast Companion is an interactive, conversation-first study tool designed to help learners deeply understand ideas from long-form podcasts. It uses retrieval-augmented generation to answer questions directly from the audio transcripts, allowing users to ask natural follow-ups and instantly verify the AI's claims by listening to the exact source audio.

📺 **[Watch the Demo Video](https://www.loom.com/share/990ba09fd2204f0ea068ba68463f115e)**

## Core experience
The core workflow is **Ask → Understand → Verify → Listen/Explore**. Instead of browsing a static episode catalogue, the user interacts conversationally. When a question is asked, the system retrieves relevant transcript evidence, generates a grounded explanation, and provides precise timestamps. The user can then click the source cards to immediately listen to that exact moment in the podcast, ensuring the AI's answers are verifiable and trustworthy.

## Features
- conversational questions
- contextual follow-ups
- collection-level discovery
- source-grounded answers
- timestamped evidence
- audio playback from cited timestamps
- cross-episode questions/comparisons
- grounded refusal when evidence is insufficient

## Architecture
Frontend (React/Vite) → FastAPI Backend → Conversational State Management → Vector Retrieval (ChromaDB) → Evidence-Grounded Generation (OpenRouter/LLM). The architecture is intentionally simple, prioritizing reliable semantic resolution and exact transcript grounding over complex orchestration.

## Prerequisites
- Python 3.10+
- Node.js 18+
- `ffmpeg` installed on your system (required for processing raw audio)
- An OpenRouter API Key
- The supplied raw Fermi Podcast audio files. **You must place the `.mp3` files in the `Podcast/` folder.** (Audio files are ignored in Git to prevent huge uploads).
  - *Note: To save your processing time, the generated JSON transcripts and vector database indexes are already included in the `data/` folder. They were generated directly from the raw audio using this system's built-in pipeline.*

## Setup

**1. Clone and enter the repository:**
```bash
cd fermi-companion
```

**2. Set up the backend (Windows):**
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
*(For macOS/Linux, use `source .venv/bin/activate` instead)*

**3. Set up the frontend:**
```bash
cd frontend
npm install
cd ..
```

## Environment
Copy `.env.example` to a new file named `.env`:
```bash
cp .env.example .env
```
Edit `.env` and configure your `OPENROUTER_API_KEY`.

## Note on Using Your Own Audio
This system complies with the assignment constraint to start directly from raw audio. It includes a built-in transcription pipeline (`src/transcribe.py`) that uses the Gemini 2.5 Flash model via OpenRouter to transcribe the audio and generate timestamps. 

If you want to test the system with your own audio files (3 or any other number):
1. **CRITICAL:** You MUST delete the pre-generated contents of the `data/` directory (transcripts, chunks, metadata, and the chroma_db folder). If you do not delete the old data, the system will mix the previous 16 podcasts' evidence with your new audio, leading to completely incorrect outputs and timestamp mismatches!
2. Clear out the `Podcast/` directory and place your own `.mp3` podcast files there.
3. Run the artifact pipeline sequentially to generate the transcripts, metadata, chunks, and vector index from scratch:

```bash
# 1. Transcribe the raw audio
python -m src.transcribe

# 2. Extract structured metadata from the transcripts
python -m src.metadata

# 3. Chunk the transcripts for retrieval
python -m src.chunker

# 4. Embed the chunks into the vector database
python -m src.retrieval build
```
*(Warning: The transcription step sends audio to the OpenRouter API and takes considerable time depending on the length of the audio. If you just want to run the application immediately, leave the existing pre-generated artifacts in the `data/` directory.)*

## Run
To run the full stack (Frontend + Backend) with a single command, execute from the root directory:
```bash
npm run dev
```
*(Note: A `package.json` in the root directory manages both concurrently. If you prefer separate terminals, run `uvicorn src.api:app --reload` in the root and `npm run dev` in the frontend directory).*

## Evaluation
To run the automated programmatic evaluation suite:
```bash
python -m src.evaluate --name final_evaluation
```
- The `--name` argument simply sets the prefix for the output JSON results file (e.g., `eval_final_evaluation_20260817_120000.json`).
- Raw evaluation results are written to `eval/results/`.

## Project structure
```
fermi-companion/
├── src/                # Backend Python source code (API, retrieval, companion logic)
├── frontend/           # React frontend
├── data/               # Transcripts, chunks, metadata, and vector DB
├── Podcast/            # Raw audio files
├── eval/               # Evaluation artifacts and scripts
├── requirements.txt    # Python dependencies
├── package.json        # Root launcher
└── README.md
```

## Notes
- **Source Material Constraint:** The system uses the supplied assignment audio as the ground truth. It strictly abides by the requirement and does *not* use YouTube closed captions or external transcript APIs as input. All transcripts were generated locally from the raw audio files using the included pipeline.
- **Catalogue Size:** The assignment brief stated "You will receive 3 raw Fermi Podcast audio files, totalling no more than 3 hours." However, I was provided with 16 podcasts totaling more than 9 hours. The system I built is dynamically configurable and safely handles this expanded catalogue without hardcoded limits.
