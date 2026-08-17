"""
Fermi Companion - Transcription Pipeline
Transcribes podcast audio using Gemini 2.5 Flash via OpenRouter.

Strategy:
1. Split each episode into ~5 minute audio segments using ffmpeg
2. Send each segment to Gemini with audio input
3. Ask for timestamped transcript output
4. Merge segments with offset-corrected timestamps
5. Save as structured JSON per episode

Usage:
    python -m src.transcribe                    # Transcribe all episodes
    python -m src.transcribe --episode 1        # Transcribe episode 1 only
    python -m src.transcribe --episode 1 --verify  # Transcribe and print sample for verification
"""

import json
import subprocess
import sys
import time
import base64
import re
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict

from src.config import (
    PODCAST_DIR, TRANSCRIPTS_DIR, DATA_DIR,
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL
)

import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()

# --- Data structures ---

@dataclass
class TranscriptSegment:
    """A single timestamped segment of transcript."""
    start_time: float  # seconds from episode start
    end_time: float    # seconds from episode start
    text: str
    episode_id: str
    segment_index: int

    @property
    def start_timestamp(self) -> str:
        """Format as MM:SS"""
        m, s = divmod(int(self.start_time), 60)
        return f"{m:02d}:{s:02d}"

    @property
    def end_timestamp(self) -> str:
        m, s = divmod(int(self.end_time), 60)
        return f"{m:02d}:{s:02d}"


@dataclass
class EpisodeTranscript:
    """Complete transcript for one episode."""
    episode_id: str
    filename: str
    title: str
    duration_seconds: float
    segments: list  # list of TranscriptSegment dicts
    transcription_model: str
    transcription_date: str


# --- Audio splitting ---

SEGMENT_DURATION_SEC = 300  # 5 minute segments for API calls


def get_audio_duration(audio_path: Path) -> float:
    """Get audio duration in seconds using ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(audio_path)],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def split_audio_segment(audio_path: Path, start_sec: float, duration_sec: float, output_path: Path) -> Path:
    """Extract a segment from an audio file using ffmpeg."""
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(audio_path),
         "-ss", str(start_sec), "-t", str(duration_sec),
         "-acodec", "libmp3lame", "-ab", "64k",  # Compress to reduce upload size
         "-ar", "16000",  # 16kHz mono for speech
         "-ac", "1",
         str(output_path)],
        capture_output=True, text=True, check=True
    )
    return output_path


def split_episode_into_segments(audio_path: Path, temp_dir: Path) -> list:
    """Split an episode into segments, returns list of (segment_path, start_offset_sec)."""
    duration = get_audio_duration(audio_path)
    segments = []
    start = 0.0

    while start < duration:
        seg_duration = min(SEGMENT_DURATION_SEC, duration - start)
        seg_path = temp_dir / f"seg_{int(start):06d}.mp3"
        split_audio_segment(audio_path, start, seg_duration, seg_path)
        segments.append((seg_path, start, seg_duration))
        start += SEGMENT_DURATION_SEC

    return segments, duration


# --- Gemini transcription ---

TRANSCRIPTION_PROMPT = """You are transcribing a podcast episode segment. This is from the "Great Papers" series by Fermi Podcast, where hosts discuss landmark scientific papers.

Produce a verbatim transcript of the audio. Include all spoken words faithfully.

Format your output as a series of timestamped blocks. Each block should cover approximately 30 seconds of speech.

Use this exact format for each block:

[MM:SS]
<spoken text for approximately 30 seconds>

[MM:SS]
<next block of spoken text>

Rules:
- Timestamps are relative to THE START OF THIS AUDIO SEGMENT (starting from 00:00)
- Include all spoken words, including filler words (um, uh, you know, etc.) where they appear
- Preserve scientific terminology accurately
- If you hear a name, try to spell it correctly
- Do not add commentary, notes, or descriptions of sounds
- Do not summarize — transcribe verbatim
- Each block should be approximately 30 seconds of speech
- Start the first block at [00:00]
"""


def transcribe_audio_segment(audio_path: Path, segment_offset_sec: float, episode_id: str, retries: int = 3) -> list:
    """
    Send an audio segment to Gemini 2.5 Flash and get timestamped transcript back.
    Returns list of TranscriptSegment objects with offset-corrected timestamps.
    """
    # Read and base64 encode the audio
    audio_bytes = audio_path.read_bytes()
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    # Build the multimodal message
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": audio_b64,
                        "format": "mp3"
                    }
                },
                {
                    "type": "text",
                    "text": TRANSCRIPTION_PROMPT
                }
            ]
        }
    ]

    for attempt in range(retries):
        try:
            response = httpx.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "google/gemini-2.5-flash",
                    "messages": messages,
                    "max_tokens": 16000,
                    "temperature": 0.0,
                },
                timeout=180,  # 3 minutes for transcription
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return parse_timestamped_transcript(content, segment_offset_sec, episode_id)
            elif response.status_code == 429:
                wait = (attempt + 1) * 10
                console.print(f"[yellow]Rate limited, waiting {wait}s...[/yellow]")
                time.sleep(wait)
            else:
                console.print(f"[red]API error {response.status_code}: {response.text[:200]}[/red]")
                if attempt < retries - 1:
                    time.sleep(5)

        except httpx.TimeoutException:
            console.print(f"[yellow]Timeout on attempt {attempt + 1}, retrying...[/yellow]")
            time.sleep(5)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            if attempt < retries - 1:
                time.sleep(5)

    console.print(f"[red]Failed to transcribe segment after {retries} attempts[/red]")
    return []


def parse_timestamped_transcript(raw_text: str, offset_sec: float, episode_id: str) -> list:
    """
    Parse Gemini's timestamped output into TranscriptSegment objects.
    Expected format: [MM:SS]\ntext\n\n[MM:SS]\ntext...
    Adjusts timestamps by adding the segment offset.
    """
    segments = []
    # Match [MM:SS] or [H:MM:SS] patterns
    pattern = r'\[(\d{1,2}):(\d{2})\]'
    blocks = re.split(pattern, raw_text)

    # blocks will be: [preamble, min1, sec1, text1, min2, sec2, text2, ...]
    if len(blocks) < 4:
        # Fallback: treat entire text as one segment
        text = raw_text.strip()
        if text:
            segments.append(TranscriptSegment(
                start_time=offset_sec,
                end_time=offset_sec + 30,
                text=text,
                episode_id=episode_id,
                segment_index=0
            ))
        return segments

    i = 1  # Skip preamble
    seg_idx = 0
    while i + 2 < len(blocks):
        minutes = int(blocks[i])
        seconds = int(blocks[i + 1])
        text = blocks[i + 2].strip()

        local_time_sec = minutes * 60 + seconds
        abs_start = offset_sec + local_time_sec

        # Look ahead for next timestamp to determine end time
        if i + 5 < len(blocks):
            next_min = int(blocks[i + 3])
            next_sec = int(blocks[i + 4])
            abs_end = offset_sec + next_min * 60 + next_sec
        else:
            # Last segment: estimate 30 seconds
            abs_end = abs_start + 30

        if text:
            segments.append(TranscriptSegment(
                start_time=abs_start,
                end_time=abs_end,
                text=text,
                episode_id=episode_id,
                segment_index=seg_idx
            ))
            seg_idx += 1

        i += 3

    return segments


# --- Episode-level transcription ---

def parse_episode_id(filename: str) -> str:
    """Extract episode ID from filename like 'Great Papers 01 - ...'"""
    match = re.match(r'Great Papers (\d+)', filename)
    if match:
        return f"ep{int(match.group(1)):02d}"
    return filename.replace(" ", "_").replace(".", "_")


def parse_episode_title(filename: str) -> str:
    """Extract readable title from filename."""
    # Remove extension and 'Great Papers XX - ' prefix
    name = Path(filename).stem
    match = re.match(r'Great Papers \d+ - (.+)', name)
    if match:
        title = match.group(1).replace("_s ", "'s ").replace("_", "'")
    else:
        title = name
    # Strip non-ASCII characters to prevent Windows console errors (e.g., Gödel)
    return title.encode("ascii", "ignore").decode("ascii")


def transcribe_episode(audio_path: Path, force: bool = False) -> EpisodeTranscript:
    """Transcribe a single episode, saving the result to JSON."""
    episode_id = parse_episode_id(audio_path.name)
    title = parse_episode_title(audio_path.name)
    output_path = TRANSCRIPTS_DIR / f"{episode_id}_transcript.json"

    # Skip if already transcribed
    if output_path.exists() and not force:
        console.print(f"[dim]Skipping {episode_id} ({title}) - already transcribed[/dim]")
        with open(output_path) as f:
            data = json.load(f)
        return EpisodeTranscript(**data)

    console.print(f"\n[bold blue]Transcribing: {title}[/bold blue] ({episode_id})")

    # Create temp directory for audio segments
    temp_dir = DATA_DIR / "temp_audio"
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Split into segments
        console.print("  Splitting audio...")
        audio_segments, total_duration = split_episode_into_segments(audio_path, temp_dir)
        console.print(f"  Duration: {total_duration:.0f}s ({total_duration/60:.1f} min), {len(audio_segments)} segments")

        # Transcribe each segment
        all_transcript_segments = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"  Transcribing {episode_id}", total=len(audio_segments))

            for seg_path, start_offset, seg_duration in audio_segments:
                segments = transcribe_audio_segment(seg_path, start_offset, episode_id)
                all_transcript_segments.extend(segments)
                progress.advance(task)
                # Small delay between API calls to avoid rate limits
                time.sleep(1)

        # Re-index segments sequentially
        for i, seg in enumerate(all_transcript_segments):
            seg.segment_index = i

        # Build episode transcript
        from datetime import datetime
        transcript = EpisodeTranscript(
            episode_id=episode_id,
            filename=audio_path.name,
            title=title,
            duration_seconds=total_duration,
            segments=[asdict(s) for s in all_transcript_segments],
            transcription_model="google/gemini-2.5-flash",
            transcription_date=datetime.now().isoformat()
        )

        # Save
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(asdict(transcript), f, indent=2, ensure_ascii=False)

        console.print(f"  [green]OK Saved {len(all_transcript_segments)} segments to {output_path.name}[/green]")
        return transcript

    finally:
        # Clean up temp audio files
        for f in temp_dir.glob("seg_*.mp3"):
            f.unlink()


# --- Main ---

def discover_episodes() -> list:
    """Find all podcast audio files in the Podcast directory."""
    audio_files = sorted(PODCAST_DIR.glob("*.mp3"))
    if not audio_files:
        console.print("[red]No MP3 files found in Podcast/ directory[/red]")
        sys.exit(1)
    return audio_files


def main():
    parser = argparse.ArgumentParser(description="Transcribe Fermi Podcast episodes")
    parser.add_argument("--episode", type=int, help="Transcribe specific episode number (1-16)")
    parser.add_argument("--force", action="store_true", help="Re-transcribe even if output exists")
    parser.add_argument("--verify", action="store_true", help="Print sample segments for verification")
    args = parser.parse_args()

    audio_files = discover_episodes()
    console.print(f"[bold]Found {len(audio_files)} episodes in Podcast/[/bold]")

    if args.episode:
        # Filter to specific episode
        target = f"Great Papers {args.episode:02d}"
        audio_files = [f for f in audio_files if target in f.name]
        if not audio_files:
            console.print(f"[red]Episode {args.episode} not found[/red]")
            sys.exit(1)

    for audio_path in audio_files:
        transcript = transcribe_episode(audio_path, force=args.force)

        if args.verify and transcript.segments:
            console.print(f"\n[bold yellow]Sample transcript for {transcript.episode_id}:[/bold yellow]")
            # Show first 5 segments
            for seg in transcript.segments[:5]:
                if isinstance(seg, dict):
                    st = seg.get("start_time", 0)
                    et = seg.get("end_time", 0)
                    text = seg.get("text", "")
                else:
                    st, et, text = seg.start_time, seg.end_time, seg.text
                m1, s1 = divmod(int(st), 60)
                m2, s2 = divmod(int(et), 60)
                console.print(f"  [{m1:02d}:{s1:02d} - {m2:02d}:{s2:02d}] {text[:150]}...")
            console.print(f"  ... ({len(transcript.segments)} total segments)")

    console.print("\n[bold green]Transcription complete![/bold green]")


if __name__ == "__main__":
    main()
