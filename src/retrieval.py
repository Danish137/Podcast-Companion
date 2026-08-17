"""
Fermi Companion - Retrieval Index
Builds and queries a ChromaDB vector index over transcript chunks.

Two conceptual levels:
1. Episode-level: uses episode metadata for discovery/recommendation
2. Passage-level: uses transcript chunks for evidence/explanation

Usage:
    python -m src.retrieval build              # Build/rebuild the index
    python -m src.retrieval query "question"   # Test a retrieval query
    python -m src.retrieval query "question" --episodes  # Episode-level query
"""

import json
import argparse
from pathlib import Path

import chromadb
from chromadb.config import Settings

from src.config import (
    CHUNKS_DIR, METADATA_DIR, INDEX_DIR,
    TOP_K_PASSAGES, TOP_K_EPISODES
)
from rich.console import Console

console = Console()

# ChromaDB persistent client
CHROMA_PATH = str(INDEX_DIR / "chroma_db")


def get_chroma_client():
    """Get or create the ChromaDB client."""
    return chromadb.PersistentClient(path=CHROMA_PATH)


def build_passage_index(force: bool = False):
    """Build the passage-level ChromaDB collection from chunks."""
    client = get_chroma_client()

    collection_name = "passages"

    if force:
        try:
            client.delete_collection(collection_name)
        except Exception:
            pass

    # Check if collection exists and has data
    try:
        collection = client.get_collection(collection_name)
        if collection.count() > 0 and not force:
            console.print(f"[dim]Passage index already exists ({collection.count()} documents). Use --force to rebuild.[/dim]")
            return collection
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    # Load all chunk files
    chunk_files = sorted(CHUNKS_DIR.glob("ep*_chunks.json"))
    if not chunk_files:
        console.print("[red]No chunk files found. Run chunking first.[/red]")
        return collection

    console.print(f"[blue]Building passage index from {len(chunk_files)} episode(s)...[/blue]")

    total_added = 0
    for cf in chunk_files:
        with open(cf, encoding="utf-8") as f:
            chunks = json.load(f)

        if not chunks:
            continue

        # Batch add to ChromaDB
        ids = [c["chunk_id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [{
            "episode_id": c["episode_id"],
            "episode_title": c["episode_title"],
            "start_time": c["start_time"],
            "end_time": c["end_time"],
            "word_count": c["word_count"],
            "duration_seconds": c["duration_seconds"],
        } for c in chunks]

        # Add in batches of 100
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_docs = documents[i:i + batch_size]
            batch_meta = metadatas[i:i + batch_size]
            collection.add(ids=batch_ids, documents=batch_docs, metadatas=batch_meta)

        total_added += len(ids)
        console.print(f"  Added {len(ids)} chunks from {chunks[0]['episode_id']}")

    console.print(f"[green]OK Passage index: {total_added} chunks indexed[/green]")
    return collection


def build_episode_index(force: bool = False):
    """Build the episode-level ChromaDB collection from metadata."""
    client = get_chroma_client()

    collection_name = "episodes"

    if force:
        try:
            client.delete_collection(collection_name)
        except Exception:
            pass

    try:
        collection = client.get_collection(collection_name)
        if collection.count() > 0 and not force:
            console.print(f"[dim]Episode index already exists ({collection.count()} documents). Use --force to rebuild.[/dim]")
            return collection
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    # Load manifest
    manifest_path = METADATA_DIR / "episode_manifest.json"
    if not manifest_path.exists():
        console.print("[red]No episode manifest found. Run metadata generation first.[/red]")
        return collection

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    console.print(f"[blue]Building episode index from {len(manifest)} episodes...[/blue]")

    ids = []
    documents = []
    metadatas = []

    for ep in manifest:
        ep_id = ep["episode_id"]
        # Create a rich text document for the episode that combines all searchable info
        concepts = ep.get("key_concepts", [])
        disciplines = ep.get("disciplines", [])
        doc_text = (
            f"Episode: {ep.get('episode_title', '')}\n"
            f"Paper: {ep.get('paper_title', '')}\n"
            f"Authors: {', '.join(ep.get('authors', []))}\n"
            f"Year: {ep.get('publication_year', '')}\n"
            f"Field: {ep.get('field', '')}\n"
            f"Disciplines: {', '.join(disciplines)}\n"
            f"Key concepts: {', '.join(concepts)}\n"
            f"Summary: {ep.get('summary', '')}"
        )

        ids.append(ep_id)
        documents.append(doc_text)
        metadatas.append({
            "episode_title": ep.get("episode_title", ""),
            "paper_title": ep.get("paper_title", ""),
            "field": ep.get("field", ""),
            "publication_year": ep.get("publication_year", 0) or 0,
            "duration_seconds": ep.get("duration_seconds", 0),
            "authors": json.dumps(ep.get("authors", [])),
            "disciplines": json.dumps(disciplines),
            "key_concepts": json.dumps(concepts),
        })

    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    console.print(f"[green]OK Episode index: {len(ids)} episodes indexed[/green]")
    return collection


# --- Query functions ---

def query_passages(query: str, top_k: int = TOP_K_PASSAGES, episode_filter: str = None) -> list:
    """
    Retrieve relevant transcript passages for a query.
    Returns list of dicts with: chunk_id, text, episode_id, episode_title, start_time, end_time, score
    """
    client = get_chroma_client()
    try:
        collection = client.get_collection("passages")
    except Exception:
        console.print("[red]Passage index not found. Run 'python -m src.retrieval build' first.[/red]")
        return []

    where_filter = None
    if episode_filter:
        where_filter = {"episode_id": episode_filter}

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"]
    )

    passages = []
    if results and results["ids"] and results["ids"][0]:
        for i, chunk_id in enumerate(results["ids"][0]):
            passages.append({
                "chunk_id": chunk_id,
                "text": results["documents"][0][i],
                "episode_id": results["metadatas"][0][i]["episode_id"],
                "episode_title": results["metadatas"][0][i]["episode_title"],
                "start_time": results["metadatas"][0][i]["start_time"],
                "end_time": results["metadatas"][0][i]["end_time"],
                "score": 1 - results["distances"][0][i],  # Convert distance to similarity
            })

    return passages


def query_episodes(query: str, top_k: int = TOP_K_EPISODES) -> list:
    """
    Retrieve relevant episodes for a discovery/comparison query.
    Returns list of dicts with episode metadata and relevance score.
    """
    client = get_chroma_client()
    try:
        collection = client.get_collection("episodes")
    except Exception:
        console.print("[red]Episode index not found. Run 'python -m src.retrieval build' first.[/red]")
        return []

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    episodes = []
    if results and results["ids"] and results["ids"][0]:
        for i, ep_id in enumerate(results["ids"][0]):
            meta = results["metadatas"][0][i]
            episodes.append({
                "episode_id": ep_id,
                "episode_title": meta["episode_title"],
                "paper_title": meta["paper_title"],
                "field": meta["field"],
                "publication_year": meta["publication_year"],
                "score": 1 - results["distances"][0][i],
                "authors": json.loads(meta.get("authors", "[]")),
                "disciplines": json.loads(meta.get("disciplines", "[]")),
                "key_concepts": json.loads(meta.get("key_concepts", "[]")),
            })

    return episodes


def query_passages_multi_episode(query: str, episode_ids: list, top_k_per_episode: int = 4) -> dict:
    """
    Retrieve passages from specific episodes for comparison queries.
    Returns dict mapping episode_id -> list of passages.
    """
    result = {}
    for ep_id in episode_ids:
        passages = query_passages(query, top_k=top_k_per_episode, episode_filter=ep_id)
        if passages:
            result[ep_id] = passages
    return result


# --- Main CLI ---

def main():
    parser = argparse.ArgumentParser(description="Build and query retrieval index")
    subparsers = parser.add_subparsers(dest="command")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build the retrieval index")
    build_parser.add_argument("--force", action="store_true", help="Rebuild even if exists")

    # Query command
    query_parser = subparsers.add_parser("query", help="Test a retrieval query")
    query_parser.add_argument("text", help="Query text")
    query_parser.add_argument("--episodes", action="store_true", help="Query episode index instead of passages")
    query_parser.add_argument("--top-k", type=int, default=5, help="Number of results")

    args = parser.parse_args()

    if args.command == "build":
        build_passage_index(force=args.force)
        build_episode_index(force=args.force)

    elif args.command == "query":
        if args.episodes:
            results = query_episodes(args.text, top_k=args.top_k)
            console.print(f"\n[bold]Episode results for: '{args.text}'[/bold]\n")
            for r in results:
                console.print(
                    f"  [{r['score']:.3f}] {r['episode_id']} - {r['episode_title']} "
                    f"({r['field']}, {r['publication_year']})"
                )
                concepts = r.get("key_concepts", [])[:5]
                if concepts:
                    console.print(f"         Concepts: {', '.join(concepts)}")
        else:
            results = query_passages(args.text, top_k=args.top_k)
            console.print(f"\n[bold]Passage results for: '{args.text}'[/bold]\n")
            for r in results:
                m1, s1 = divmod(int(r["start_time"]), 60)
                m2, s2 = divmod(int(r["end_time"]), 60)
                console.print(
                    f"  [{r['score']:.3f}] {r['episode_id']} "
                    f"[{m1:02d}:{s1:02d}-{m2:02d}:{s2:02d}] "
                    f"{r['episode_title']}"
                )
                console.print(f"         {r['text'][:150]}...")
                console.print()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
