"""
Fermi Companion - FastAPI Backend
Provides a simple HTTP API for the conversational companion.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import json

from src.companion import FermiCompanion, ConversationState
from src.config import METADATA_DIR, PODCAST_DIR

app = FastAPI(title="Fermi Companion API")

# Add CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite + common dev ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

companion = FermiCompanion()

# In-memory session store for prototype
# In a real app this would be a database or Redis
sessions: Dict[str, ConversationState] = {}

class ChatRequest(BaseModel):
    session_id: str
    message: str

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

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Get or create session state
        if request.session_id not in sessions:
            sessions[request.session_id] = ConversationState()
        
        state = sessions[request.session_id]
        
        # We'll peek at the intent purely for returning it in the API response
        intent = companion.route_intent(request.message, state)
        
        # Process the message
        response_text = companion.process_message(request.message, state)
        
        # Map last retrieved evidence to structured sources
        sources = []
        # Suppress sources if the response is an explicit refusal
        if "I couldn't find enough evidence" not in response_text:
            for evidence in state.last_retrieved_evidence:
                # Extract first 200 chars of text as excerpt
                excerpt = evidence.get("text", "")
                if len(excerpt) > 200:
                    excerpt = excerpt[:200] + "..."
                
                sources.append(SourceEvidence(
                    episode_id=evidence["episode_id"],
                    episode_title=evidence["episode_title"],
                    start_time=evidence["start_time"],
                    end_time=evidence["end_time"],
                    excerpt=excerpt if excerpt else None
                ))
        
        return ChatResponse(
            response=response_text,
            intent_used=intent,
            sources=sources
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


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
        # Load manifest
        manifest_path = METADATA_DIR / "episode_manifest.json"
        if not manifest_path.exists():
            raise HTTPException(status_code=500, detail="Episode manifest not found")
        
        with open(manifest_path, encoding="utf-8") as f:
            episodes = json.load(f)
        
        # Find episode
        episode = next((ep for ep in episodes if ep["episode_id"] == episode_id), None)
        if not episode:
            raise HTTPException(status_code=404, detail=f"Episode {episode_id} not found")
        
        # Map to audio file
        audio_path = PODCAST_DIR / episode["filename"]
        if not audio_path.exists():
            raise HTTPException(status_code=404, detail=f"Audio file not found: {episode['filename']}")
        
        # Return with HTTP range support for seeking
        return FileResponse(
            path=str(audio_path),
            media_type="audio/mpeg",
            filename=episode["filename"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True)
