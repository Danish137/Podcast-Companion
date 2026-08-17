"""
Fermi Companion - Transcript Chunking
Takes timestamped transcript segments and produces retrieval-ready chunks.

Strategy:
- Merge consecutive transcript segments into chunks of target duration
- Preserve episode/timestamp provenance on every chunk
- Add contextual overlap between chunks
- Each chunk is a self-contained passage suitable for embedding

Usage:
    python -m src.chunker                    # Chunk all transcribed episodes
    python -m src.chunker --episode 1        # Chunk episode 1 only
"""

import json
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict

from src.config import (
    TRANSCRIPTS_DIR, CHUNKS_DIR,
    CHUNK_DURATION_SEC, CHUNK_OVERLAP_SEC
)
from rich.console import Console

console = Console()


@dataclass
class Chunk:
    """A retrieval-ready text chunk with full provenance."""
    chunk_id: str           # e.g., "ep01_chunk_003"
    episode_id: str         # e.g., "ep01"
    episode_title: str
    start_time: float       # seconds from episode start
    end_time: float         # seconds from episode start
    text: str               # the chunk content
    word_count: int
    duration_seconds: float

    @property
    def start_timestamp(self) -> str:
        m, s = divmod(int(self.start_time), 60)
        return f"{m:02d}:{s:02d}"

    @property
    def end_timestamp(self) -> str:
        m, s = divmod(int(self.end_time), 60)
        return f"{m:02d}:{s:02d}"


def load_transcript(transcript_path: Path) -> dict:
    """Load a transcript JSON file."""
    with open(transcript_path, encoding="utf-8") as f:
        return json.load(f)


def chunk_transcript(
    transcript: dict,
    target_duration: int = CHUNK_DURATION_SEC,
    overlap_duration: int = CHUNK_OVERLAP_SEC
) -> list:
    """
    Merge transcript segments into chunks of approximately target_duration seconds.
    
    Strategy:
    - Accumulate segments until we reach ~target_duration
    - Try to break at natural sentence boundaries
    - Add overlap from the end of the previous chunk
    """
    segments = transcript.get("segments", [])
    if not segments:
        return []

    episode_id = transcript["episode_id"]
    episode_title = transcript["title"]

    chunks = []
    current_texts = []
    current_start = segments[0]["start_time"]
    current_duration = 0
    previous_overlap_text = ""

    for i, seg in enumerate(segments):
        seg_text = seg["text"].strip()
        if not seg_text:
            continue

        seg_duration = seg["end_time"] - seg["start_time"]
        current_texts.append(seg_text)
        current_duration += seg_duration

        # Check if we should finalize this chunk
        is_last = (i == len(segments) - 1)
        reached_target = current_duration >= target_duration

        if reached_target or is_last:
            # Build chunk text
            chunk_text = " ".join(current_texts)

            # Prepend overlap from previous chunk for context
            if previous_overlap_text:
                chunk_text = previous_overlap_text + " " + chunk_text

            chunk_end = seg["end_time"]

            chunk = Chunk(
                chunk_id=f"{episode_id}_chunk_{len(chunks):03d}",
                episode_id=episode_id,
                episode_title=episode_title,
                start_time=current_start,
                end_time=chunk_end,
                text=chunk_text,
                word_count=len(chunk_text.split()),
                duration_seconds=chunk_end - current_start
            )
            chunks.append(chunk)

            # Prepare overlap for next chunk
            # Take the last ~overlap_duration seconds of text
            if not is_last:
                overlap_segments = []
                overlap_time = 0
                for j in range(len(current_texts) - 1, -1, -1):
                    overlap_segments.insert(0, current_texts[j])
                    # Estimate time based on proportion
                    seg_word_ratio = len(current_texts[j].split()) / max(len(chunk_text.split()), 1)
                    overlap_time += seg_word_ratio * current_duration
                    if overlap_time >= overlap_duration:
                        break
                previous_overlap_text = " ".join(overlap_segments)

            # Reset for next chunk
            if i + 1 < len(segments):
                current_start = segments[i + 1]["start_time"]
            current_texts = []
            current_duration = 0

    return chunks


def process_episode(transcript_path: Path, force: bool = False) -> list:
    """Chunk a single episode's transcript."""
    transcript = load_transcript(transcript_path)
    episode_id = transcript["episode_id"]
    output_path = CHUNKS_DIR / f"{episode_id}_chunks.json"

    if output_path.exists() and not force:
        console.print(f"[dim]Skipping {episode_id} - chunks already exist[/dim]")
        with open(output_path) as f:
            return json.load(f)

    console.print(f"[blue]Chunking {episode_id}: {transcript['title']}[/blue]")

    chunks = chunk_transcript(transcript)
    chunk_dicts = [asdict(c) for c in chunks]

    # Save
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunk_dicts, f, indent=2, ensure_ascii=False)

    # Stats
    word_counts = [c.word_count for c in chunks]
    durations = [c.duration_seconds for c in chunks]
    console.print(
        f"  [green]OK {len(chunks)} chunks | "
        f"avg {sum(word_counts)//len(chunks)} words | "
        f"avg {sum(durations)/len(durations):.0f}s | "
        f"range {min(durations):.0f}s-{max(durations):.0f}s[/green]"
    )

    return chunk_dicts


def main():
    parser = argparse.ArgumentParser(description="Chunk transcribed episodes")
    parser.add_argument("--episode", type=int, help="Process specific episode number")
    parser.add_argument("--force", action="store_true", help="Re-chunk even if output exists")
    parser.add_argument("--target-duration", type=int, default=CHUNK_DURATION_SEC,
                        help=f"Target chunk duration in seconds (default: {CHUNK_DURATION_SEC})")
    parser.add_argument("--overlap", type=int, default=CHUNK_OVERLAP_SEC,
                        help=f"Overlap duration in seconds (default: {CHUNK_OVERLAP_SEC})")
    args = parser.parse_args()

    # Find transcript files
    if args.episode:
        transcript_files = list(TRANSCRIPTS_DIR.glob(f"ep{args.episode:02d}_transcript.json"))
        if not transcript_files:
            console.print(f"[red]No transcript found for episode {args.episode}. Run transcription first.[/red]")
            return
    else:
        transcript_files = sorted(TRANSCRIPTS_DIR.glob("ep*_transcript.json"))
        if not transcript_files:
            console.print("[red]No transcripts found. Run transcription first.[/red]")
            return

    console.print(f"[bold]Processing {len(transcript_files)} transcript(s)[/bold]")
    console.print(f"  Target duration: {args.target_duration}s, Overlap: {args.overlap}s")

    all_chunks = []
    for tf in transcript_files:
        chunks = process_episode(tf, force=args.force)
        all_chunks.extend(chunks)

    console.print(f"\n[bold green]Total: {len(all_chunks)} chunks across {len(transcript_files)} episode(s)[/bold green]")


if __name__ == "__main__":
    main()
