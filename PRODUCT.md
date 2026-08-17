# Product Note

## Intended User
The intended user is a learner or curious individual who wants to understand specific ideas, concepts, and historical moments discussed in long-form Fermi podcasts without having to listen to entire episodes linearly. 

## Problem
Long-form audio is inherently difficult to search and study. When a learner wants to know "what pattern Mendeleev noticed" or "why a Nash Equilibrium isn't always good," they cannot easily skim a 45-minute audio file. Traditional transcripts help with search, but they lack the conversational synthesis needed for learning complex topics.

## Product Choice
A conversation-first companion was chosen rather than a generic episode catalogue, a dashboard, or a plain RAG chatbot. The key product behavior is:

**ASK → UNDERSTAND → VERIFY → LISTEN/EXPLORE**

Instead of merely answering questions, the system maintains conversational context, retrieves supporting evidence from the transcripts, exposes the exact sources and timestamps to the user, and allows the learner to instantly listen to the cited original audio. This bridges the gap between AI synthesis and the raw, engaging source material of the podcast.

## Design Principles
- **Conversation-first**: The interface immediately invites the user to ask a question rather than browse a list.
- **Source-grounded**: Every factual answer must be tied directly to a specific podcast chunk.
- **Evidence before confidence**: If the system cannot find sufficient evidence, it refuses to answer rather than hallucinating.
- **Useful abstention**: Refusals are explicit and grounded in the rules of the system.
- **Contextual follow-ups**: The system remembers the conversational topic and episode focus to naturally resolve pronouns and follow-up inquiries.
- **Audio as the final source of truth**: Text synthesis is temporary; the podcast audio is the primary learning artifact. The UI makes the audio playable at the exact moment of the cited evidence.
