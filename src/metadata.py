"""
Fermi Companion - Episode Metadata Generator
Generates structured metadata for each episode from its transcript.

For each episode, produces:
- paper title
- authors
- publication year
- field/discipline
- key concepts (5-10)
- short summary (2-3 sentences)

Uses Gemini to extract metadata from the transcript content.

Usage:
    python -m src.metadata                   # Generate metadata for all transcribed episodes
    python -m src.metadata --episode 1       # Generate for episode 1 only
"""

import json
import argparse
import time
from pathlib import Path

from src.config import (
    TRANSCRIPTS_DIR, METADATA_DIR,
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL
)

import httpx
from rich.console import Console

console = Console()

METADATA_PROMPT = """You are analyzing a transcript from the "Great Papers" podcast series by Fermi Podcast. Each episode discusses one landmark scientific paper.

Based on the transcript content below, extract the following metadata. Be accurate — only include information that is clearly discussed in the transcript.

Respond in this exact JSON format (no markdown, just raw JSON):
{{
  "paper_title": "The original paper's title as discussed in the podcast",
  "authors": ["Author 1", "Author 2"],
  "publication_year": 1905,
  "field": "Physics",
  "subfield": "Special Relativity",
  "key_concepts": ["concept1", "concept2", "concept3", "concept4", "concept5"],
  "summary": "2-3 sentence summary of what the podcast discusses about this paper",
  "disciplines": ["Physics", "Mathematics"]
}}

Rules:
- "field" should be the primary discipline (Physics, Biology, Computer Science, Mathematics, Chemistry, Information Theory, Game Theory, etc.)
- "disciplines" should list all disciplines touched on in the discussion
- "key_concepts" should be 5-10 key scientific concepts discussed
- "summary" should describe what the PODCAST DISCUSSES, not what the paper establishes
- If uncertain about a field, use the most accurate description based on the transcript
- Do not invent information not present in the transcript

Here is the episode transcript (first ~3000 words):

{transcript_excerpt}
"""


def get_transcript_excerpt(transcript: dict, max_words: int = 3000) -> str:
    """Get the first ~max_words of transcript text for metadata extraction."""
    segments = transcript.get("segments", [])
    words = []
    for seg in segments:
        text = seg.get("text", "").strip()
        if text:
            words.extend(text.split())
        if len(words) >= max_words:
            break
    return " ".join(words[:max_words])


def extract_metadata(transcript: dict, retries: int = 3) -> dict:
    """Use Gemini to extract structured metadata from a transcript."""
    excerpt = get_transcript_excerpt(transcript)
    episode_id = transcript["episode_id"]
    title = transcript["title"]

    # Start with what we can parse from the filename
    base_metadata = {
        "episode_id": episode_id,
        "episode_title": title,
        "filename": transcript["filename"],
        "duration_seconds": transcript["duration_seconds"],
        "segment_count": len(transcript.get("segments", [])),
    }

    if not excerpt:
        console.print(f"  [yellow]No transcript text available for {episode_id}[/yellow]")
        base_metadata.update({
            "paper_title": title,
            "authors": [],
            "publication_year": None,
            "field": "Unknown",
            "subfield": "Unknown",
            "key_concepts": [],
            "summary": "Transcript not yet available.",
            "disciplines": []
        })
        return base_metadata

    prompt = METADATA_PROMPT.format(transcript_excerpt=excerpt)

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
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000,
                    "temperature": 0.0,
                },
                timeout=60,
            )

            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                # Parse JSON from response (strip markdown code fences if present)
                content = content.strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[1]
                    content = content.rsplit("```", 1)[0]
                content = content.strip()

                extracted = json.loads(content)
                base_metadata.update(extracted)
                return base_metadata

            elif response.status_code == 429:
                wait = (attempt + 1) * 10
                console.print(f"  [yellow]Rate limited, waiting {wait}s...[/yellow]")
                time.sleep(wait)
            else:
                console.print(f"  [red]API error {response.status_code}: {response.text[:200]}[/red]")
                time.sleep(5)

        except json.JSONDecodeError as e:
            console.print(f"  [yellow]JSON parse error on attempt {attempt + 1}: {e}[/yellow]")
            time.sleep(3)
        except Exception as e:
            console.print(f"  [red]Error: {e}[/red]")
            time.sleep(5)

    # Fallback: minimal metadata from filename
    console.print(f"  [yellow]Using fallback metadata for {episode_id}[/yellow]")
    base_metadata.update({
        "paper_title": title,
        "authors": [],
        "publication_year": None,
        "field": "Unknown",
        "subfield": "Unknown",
        "key_concepts": [],
        "summary": f"Podcast discussion of {title}.",
        "disciplines": []
    })
    return base_metadata


def generate_episode_metadata(transcript_path: Path, force: bool = False) -> dict:
    """Generate metadata for a single episode."""
    with open(transcript_path, encoding="utf-8") as f:
        transcript = json.load(f)

    episode_id = transcript["episode_id"]
    output_path = METADATA_DIR / f"{episode_id}_metadata.json"

    if output_path.exists() and not force:
        console.print(f"[dim]Skipping {episode_id} - metadata already exists[/dim]")
        with open(output_path) as f:
            return json.load(f)

    console.print(f"[blue]Extracting metadata: {transcript['title']}[/blue]")
    metadata = extract_metadata(transcript)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    console.print(f"  [green]OK {metadata.get('field', '?')} | {metadata.get('paper_title', '?')} ({metadata.get('publication_year', '?')})[/green]")
    concepts = metadata.get("key_concepts", [])
    if concepts:
        console.print(f"  Concepts: {', '.join(concepts[:7])}")

    return metadata


def build_episode_manifest(metadata_dir: Path = METADATA_DIR):
    """Build a combined manifest of all episodes."""
    manifest_path = metadata_dir / "episode_manifest.json"
    metadata_files = sorted(metadata_dir.glob("ep*_metadata.json"))

    if not metadata_files:
        console.print("[yellow]No metadata files found[/yellow]")
        return

    manifest = []
    for mf in metadata_files:
        with open(mf) as f:
            manifest.append(json.load(f))

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    console.print(f"\n[bold green]Episode manifest: {len(manifest)} episodes saved to {manifest_path.name}[/bold green]")

    # Summary table
    console.print("\n[bold]Episode Manifest:[/bold]")
    for ep in manifest:
        field = ep.get("field", "?")
        year = ep.get("publication_year", "?")
        paper = ep.get("paper_title", ep.get("episode_title", "?"))
        dur = ep.get("duration_seconds", 0)
        console.print(f"  {ep['episode_id']} | {field:<20} | {year} | {paper} ({dur/60:.0f}min)")


def main():
    parser = argparse.ArgumentParser(description="Generate episode metadata from transcripts")
    parser.add_argument("--episode", type=int, help="Process specific episode")
    parser.add_argument("--force", action="store_true", help="Regenerate even if exists")
    parser.add_argument("--manifest-only", action="store_true", help="Only rebuild manifest from existing metadata")
    args = parser.parse_args()

    if args.manifest_only:
        build_episode_manifest()
        return

    if args.episode:
        files = list(TRANSCRIPTS_DIR.glob(f"ep{args.episode:02d}_transcript.json"))
    else:
        files = sorted(TRANSCRIPTS_DIR.glob("ep*_transcript.json"))

    if not files:
        console.print("[red]No transcripts found. Run transcription first.[/red]")
        return

    console.print(f"[bold]Processing {len(files)} transcript(s) for metadata[/bold]")

    for tf in files:
        generate_episode_metadata(tf, force=args.force)
        time.sleep(1)  # Rate limit

    build_episode_manifest()


if __name__ == "__main__":
    main()
