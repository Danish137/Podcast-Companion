"""
Fermi Companion - FastAPI Backend
Provides a simple HTTP API for the conversational companion.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
from pathlib import Path
import threading
import time
import uvicorn
import json
import os

from src.companion import FermiCompanion, ConversationState
from src.config import METADATA_DIR, PODCAST_DIR, PROJECT_ROOT
from src.transcribe import parse_episode_id

app = FastAPI(title="Fermi Companion API")

# Allowed frontend origins: local dev by default, extend via FERMI_CORS_ORIGINS (comma-separated)
_cors_origins = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]
_cors_origins += [o.strip() for o in os.getenv("FERMI_CORS_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Every chat turn is appended here so real conversations can be reviewed later
CHAT_LOG_PATH = PROJECT_ROOT / "logs" / "chat_log.jsonl"
_log_lock = threading.Lock()


def _log_turn(record: dict) -> None:
    try:
        CHAT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _log_lock, open(CHAT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:  # logging must never break a chat response
        print(f"[ChatLog] Could not write log: {e}")


def _load_manifest() -> list:
    manifest_path = METADATA_DIR / "episode_manifest.json"
    if not manifest_path.exists():
        raise HTTPException(status_code=500, detail="Episode manifest not found")
    with open(manifest_path, encoding="utf-8") as f:
        return json.load(f)


def _resolve_audio_path(episode: dict) -> Optional[Path]:
    """
    Find the MP3 for an episode. Falls back to matching by episode number,
    because manifest filenames with non-ASCII characters (e.g. "Gödel") can be
    mis-encoded and no longer match the name on disk.
    """
    audio_path = PODCAST_DIR / episode["filename"]
    if audio_path.exists():
        return audio_path
    return next(
        (p for p in PODCAST_DIR.glob("*.mp3") if parse_episode_id(p.name) == episode["episode_id"]),
        None,
    )

companion = FermiCompanion()

# In-memory session store
sessions: Dict[str, ConversationState] = {}

class HistoryMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    session_id: str
    message: str
    # Recent turns as the browser shows them. Used only to rebuild a session the
    # server doesn't know (e.g. after a restart), so follow-ups keep their context.
    history: Optional[List[HistoryMessage]] = None


MAX_RESTORED_MESSAGES = 8
MAX_RESTORED_CHARS = 4000

class SourceEvidence(BaseModel):
    """Structured source evidence for frontend display"""
    episode_id: str
    episode_title: str
    start_time: float  # seconds
    end_time: float    # seconds
    excerpt: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    intent_used: str  # For debugging/evaluation
    sources: List[SourceEvidence] = []  # NEW: structured sources

class EpisodeSummary(BaseModel):
    episode_id: str
    episode_title: str
    paper_title: Optional[str] = None
    publication_year: Optional[int] = None
    field: Optional[str] = None
    duration_seconds: Optional[float] = None


# Plain `def` (not async): FastAPI runs it in a worker thread, so the blocking
# LLM calls don't freeze the server — audio keeps streaming while a question is answered.
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    started = time.time()
    try:
        # Get or create session state; restore context from the browser if the
        # server lost this session (sessions live in memory)
        if request.session_id not in sessions:
            restored = ConversationState()
            for msg in (request.history or [])[-MAX_RESTORED_MESSAGES:]:
                if msg.role in ("user", "assistant") and msg.content.strip():
                    restored.add_message(msg.role, msg.content[:MAX_RESTORED_CHARS])
            if restored.history:
                print(f"[State] Restored session {request.session_id[:8]} with {len(restored.history)} messages")
            sessions[request.session_id] = restored

        state = sessions[request.session_id]

        # Process the message (routes intent once, records it on state)
        response_text = companion.process_message(request.message, state)
        intent = state.last_intent or "EXPLAIN"

        # Only the passages the answer actually cites are shown as sources
        sources = []
        for evidence in state.last_cited_evidence:
            excerpt = evidence.get("text", "")
            if len(excerpt) > 280:
                excerpt = excerpt[:280].rsplit(" ", 1)[0] + "…"
            sources.append(SourceEvidence(
                episode_id=evidence["episode_id"],
                episode_title=evidence["episode_title"],
                start_time=evidence["start_time"],
                end_time=evidence["end_time"],
                excerpt=excerpt or None
            ))

        _log_turn({
            "time": datetime.now(timezone.utc).isoformat(),
            "session_id": request.session_id,
            "question": request.message,
            "intent": intent,
            "resolved_query": state.last_resolved_query,
            "episode_focus": state.current_episode_focus,
            "retrieved": [
                {"chunk_id": p.get("chunk_id"), "episode_id": p["episode_id"],
                 "start_time": p["start_time"], "score": round(p.get("score", 0), 3)}
                for p in state.last_retrieved_evidence
            ],
            "cited": [s.model_dump(exclude={"excerpt"}) for s in sources],
            "response": response_text,
            "seconds": round(time.time() - started, 2),
        })

        return ChatResponse(
            response=response_text,
            intent_used=intent,
            sources=sources
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        _log_turn({
            "time": datetime.now(timezone.utc).isoformat(),
            "session_id": request.session_id,
            "question": request.message,
            "error": str(e),
        })
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/episodes", response_model=List[EpisodeSummary])
def list_episodes():
    """Catalogue of episodes that have playable audio, for the frontend."""
    return [
        EpisodeSummary(
            episode_id=ep["episode_id"],
            episode_title=ep["episode_title"],
            paper_title=ep.get("paper_title"),
            publication_year=ep.get("publication_year"),
            field=ep.get("field"),
            duration_seconds=ep.get("duration_seconds"),
        )
        for ep in _load_manifest()
        if _resolve_audio_path(ep) is not None
    ]


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/episodes/{episode_id}/audio")
async def get_episode_audio(episode_id: str):
    """
    Serve podcast audio for source verification.
    Validates episode_id against manifest to prevent arbitrary file access.
    """
    try:
        episode = next((ep for ep in _load_manifest() if ep["episode_id"] == episode_id), None)
        if not episode:
            raise HTTPException(status_code=404, detail=f"Episode {episode_id} not found")

        audio_path = _resolve_audio_path(episode)
        if audio_path is None:
            raise HTTPException(status_code=404, detail=f"Audio file not found for {episode_id}")

        # Return with HTTP range support for seeking
        return FileResponse(
            path=str(audio_path),
            media_type="audio/mpeg",
            filename=audio_path.name,
            content_disposition_type="inline",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True)
