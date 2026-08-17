"""
Fermi Companion - Configuration
Central config loading from environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# --- Paths ---
PODCAST_DIR = PROJECT_ROOT / "Podcast"
DATA_DIR = PROJECT_ROOT / "data"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
CHUNKS_DIR = DATA_DIR / "chunks"
INDEX_DIR = DATA_DIR / "index"
METADATA_DIR = DATA_DIR / "metadata"
EVAL_DIR = PROJECT_ROOT / "eval"

# Ensure data directories exist
for d in [TRANSCRIPTS_DIR, CHUNKS_DIR, INDEX_DIR, METADATA_DIR, EVAL_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# --- API Keys ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()

if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY not set. "
        "Create a .env file in the project root with: OPENROUTER_API_KEY=sk-or-v1-..."
    )

# --- Model Configuration ---
# OpenRouter base URL for chat completions
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Default models (can be overridden via env)
CHAT_MODEL = os.getenv("FERMI_CHAT_MODEL", "google/gemini-2.5-flash")
EMBEDDING_MODEL = os.getenv("FERMI_EMBEDDING_MODEL", "text-embedding-3-small")

# --- Transcription ---
# OpenRouter doesn't proxy Whisper, so we use OpenAI-compatible Whisper API
# via a provider that supports it, or fall back to local whisper
WHISPER_MODEL = os.getenv("FERMI_WHISPER_MODEL", "whisper-1")

# --- Chunking ---
CHUNK_DURATION_SEC = int(os.getenv("FERMI_CHUNK_DURATION", "90"))
CHUNK_OVERLAP_SEC = int(os.getenv("FERMI_CHUNK_OVERLAP", "15"))

# --- Retrieval ---
TOP_K_PASSAGES = int(os.getenv("FERMI_TOP_K_PASSAGES", "8"))
TOP_K_EPISODES = int(os.getenv("FERMI_TOP_K_EPISODES", "3"))
