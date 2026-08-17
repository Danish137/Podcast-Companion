"""
Fermi Companion - Core Agent Logic
Handles conversation state, intent routing, and answer generation.
"""

import json
from typing import List, Dict, Optional
from dataclasses import dataclass, field

from src.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, CHAT_MODEL
from src.retrieval import query_passages, query_episodes, query_passages_multi_episode

import httpx

# --- Prompts ---

ROUTING_PROMPT = """You are the intent router for Fermi Companion, a study tool for podcast episodes about landmark scientific papers.
Analyze the user's latest message (and conversation history) to determine the intent.

The user's message is one of these intents:
1. "EXPLAIN": The user wants an explanation, clarification, or factual answer about a concept. (e.g., "Explain special relativity", "I don't understand the train example", "What is DNA?")
2. "COMPARE": The user explicitly asks to compare concepts across different episodes or papers. (e.g., "How do Einstein and Newton compare?", "Connect the ideas in episode 1 and 2")
3. "DISCOVER": The user is looking for recommendations on what to listen to. (e.g., "Which episodes cover biology?", "What should I listen to next?")
4. "UNSUPPORTED": The user is asking about something completely unrelated to science/the podcast, or trying to break the system. (e.g., "Write a poem", "What's the weather?")

Respond with EXACTLY ONE word from the above list (EXPLAIN, COMPARE, DISCOVER, UNSUPPORTED).
"""

GENERATION_PROMPT = """You are Fermi Companion, a knowledgeable study guide for the "Great Papers" podcast series.

Your task is to answer the user's question based STRICTLY on the provided podcast evidence.

--- PODCAST EVIDENCE ---
{evidence}
------------------------

RULES:
1. NO FABRICATION: Base your answer *only* on the provided evidence. Do not use outside knowledge.
2. CITATION: You MUST cite the source of your claims. Use the format: "[Episode Title, MM:SS]". (e.g., "[Einstein's Special Relativity, 14:30]")
3. MISSING INFO: If the provided evidence does not contain the answer, say "I couldn't find enough evidence of that in the supplied episodes, so I don't want to invent an answer."
4. TONE: Be helpful, encouraging, and clear. Act like a study companion, not a robot.
5. CONTEXT: Consider the user's previous questions (if any) to provide a coherent follow-up.

User's Question: {question}
"""

DISCOVERY_PROMPT = """You are Fermi Companion, a knowledgeable study guide for the "Great Papers" podcast series.

Your task is to act as a recommendation engine. You are provided with the complete catalogue of all available episodes below.
Filter this list based on the user's request (e.g., temporal constraints like "before 1900", or categorical constraints like "biology").

--- COMPLETE EPISODE CATALOGUE ---
{evidence}
----------------------------------

RULES:
1. NO FABRICATION: Only recommend episodes that are explicitly present in the provided catalogue.
2. EXHAUSTIVE MATCHING: Recommend *all* episodes from the catalogue that match the user's criteria.
3. EXPLANATION: Briefly explain *why* each recommended episode matches based on its metadata (field, concepts, year).
4. MISSING INFO: If zero episodes match the request, honestly state that the podcast collection doesn't cover that topic.

User's Question: {question}
"""

REWRITE_PROMPT = """You are a conversational query rewriter.
Your task is to take the user's latest message and rewrite it into a fully self-contained search query.
If the user's message contains pronouns (it, that, he, etc.) or conversational references ("that part", "there"), resolve them using the conversation history.

If the user is asking about a specific podcast episode mentioned in the history, include the episode title or topic in the search query.
If the user changes the topic completely, set "topic_switch" to true.

Respond strictly with a JSON object in this format:
{
  "rewritten_query": "The fully resolved query",
  "topic_switch": boolean
}
"""


# --- State Management ---

@dataclass
class ConversationState:
    history: List[Dict[str, str]] = field(default_factory=list)
    last_retrieved_evidence: List[dict] = field(default_factory=list)
    current_episode_focus: Optional[str] = None
    last_resolved_query: Optional[str] = None

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})


# --- Core Logic ---

class FermiCompanion:
    def __init__(self):
        self.client = httpx.Client(
            base_url=OPENROUTER_BASE_URL,
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            timeout=60.0
        )

    def _call_llm(self, messages: List[dict], max_tokens: int = 1000) -> str:
        """Helper to call OpenRouter."""
        response = self.client.post(
            "/chat/completions",
            json={
                "model": CHAT_MODEL,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.2
            }
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    def route_intent(self, question: str, state: ConversationState) -> str:
        """Determine the user's intent."""
        # Simple history formatting for context
        history_text = ""
        for msg in state.history[-4:]: # Last 2 turns
            history_text += f"{msg['role'].capitalize()}: {msg['content']}\\n"

        prompt = f"{ROUTING_PROMPT}\\n\\nHistory:\\n{history_text}\\nUser: {question}"
        messages = [{"role": "user", "content": prompt}]
        
        intent = self._call_llm(messages, max_tokens=10).upper()
        
        # Fallback handling
        valid_intents = ["EXPLAIN", "COMPARE", "DISCOVER", "UNSUPPORTED"]
        for valid in valid_intents:
            if valid in intent:
                return valid
        return "EXPLAIN" # Default

    def rewrite_query(self, question: str, state: ConversationState) -> tuple[str, bool]:
        """Rewrite query resolving conversational references."""
        if not state.history:
            return question, False
            
        history_text = ""
        for msg in state.history[-4:]:
            history_text += f"{msg['role'].capitalize()}: {msg['content']}\n"
            
        prompt = f"{REWRITE_PROMPT}\n\nHistory:\n{history_text}\nUser: {question}"
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self._call_llm(messages, max_tokens=150)
            import re
            json_match = re.search(r'\{.*\}', response.replace('\n', ' '))
            if json_match:
                data = json.loads(json_match.group(0))
                return data.get("rewritten_query", question), data.get("topic_switch", False)
        except Exception as e:
            print(f"[Rewriter Error] {e}")
            
        return question, False

    def format_passage_evidence(self, passages: list) -> str:
        """Format retrieved passages for the LLM."""
        if not passages:
            return "No relevant evidence found in the transcripts."
            
        formatted = []
        for p in passages:
            m1, s1 = divmod(int(p["start_time"]), 60)
            m2, s2 = divmod(int(p["end_time"]), 60)
            time_range = f"{m1:02d}:{s1:02d}-{m2:02d}:{s2:02d}"
            formatted.append(f"Episode: {p['episode_title']}\\nTimestamp: {time_range}\\nTranscript: {p['text']}\\n")
        
        return "\\n".join(formatted)

    def format_episode_evidence(self, episodes: list) -> str:
        """Format retrieved episode metadata for the LLM."""
        if not episodes:
            return "No relevant episodes found."
            
        formatted = []
        for e in episodes:
            concepts = ", ".join(e.get("key_concepts", []))
            formatted.append(f"Title: {e['episode_title']}\\nPaper: {e['paper_title']} ({e['publication_year']})\\nField: {e['field']}\\nConcepts: {concepts}\\n")
        
        return "\\n".join(formatted)

    def process_message(self, question: str, state: ConversationState) -> str:
        """Main entry point for handling a user message."""
        
        # 1. Intent Routing
        intent = self.route_intent(question, state)
        print(f"[Router] Intent detected: {intent}")

        # 2. Retrieval & Generation based on Intent
        if intent == "UNSUPPORTED":
            response = "I couldn't find enough evidence of that in the supplied episodes, so I don't want to invent an answer."
            
        elif intent == "DISCOVER":
            # IMPROVEMENT: Bypass vector retrieval and use full manifest for exact categorical/temporal filtering
            from src.config import METADATA_DIR
            manifest_path = METADATA_DIR / "episode_manifest.json"
            if manifest_path.exists():
                with open(manifest_path, encoding="utf-8") as f:
                    episodes = json.load(f)
            else:
                episodes = []
                
            evidence_text = self.format_episode_evidence(episodes)
            prompt = DISCOVERY_PROMPT.format(evidence=evidence_text, question=question)
            
            messages = [{"role": "user", "content": prompt}]
            response = self._call_llm(messages, max_tokens=1500)
            
            # Set episode focus to the first episode mentioned in the response
            for ep in episodes:
                if ep["episode_title"].lower() in response.lower() or ep["paper_title"].lower() in response.lower():
                    state.current_episode_focus = ep["episode_id"]
                    print(f"[State] Episode focus set to: {state.current_episode_focus}")
                    break
            
        elif intent == "COMPARE":
            # 1. Find relevant episodes first
            episodes = query_episodes(question, top_k=3)
            ep_ids = [e["episode_id"] for e in episodes]
            
            # 2. Retrieve passages from those specific episodes
            multi_passages = query_passages_multi_episode(question, ep_ids, top_k_per_episode=3)
            
            # Flatten passages for context
            all_passages = []
            for ep_id, passages in multi_passages.items():
                all_passages.extend(passages)
                
            state.last_retrieved_evidence = all_passages
            evidence_text = self.format_passage_evidence(all_passages)
            prompt = GENERATION_PROMPT.format(evidence=evidence_text, question=question)
            
            messages = state.history.copy()
            messages.append({"role": "user", "content": prompt})
            response = self._call_llm(messages)
            
        else: # EXPLAIN (Default)
            resolved_query, topic_switch = self.rewrite_query(question, state)
            state.last_resolved_query = resolved_query
            print(f"[Retrieval] Resolved query: '{resolved_query}' (topic_switch: {topic_switch})")
            
            if topic_switch:
                state.current_episode_focus = None
                print("[State] Topic switch detected, cleared episode focus")
                
            passages = query_passages(resolved_query, top_k=5, episode_filter=state.current_episode_focus)
            state.last_retrieved_evidence = passages
                
            evidence_text = self.format_passage_evidence(passages)
            prompt = GENERATION_PROMPT.format(evidence=evidence_text, question=resolved_query)
            
            messages = state.history.copy()
            messages.append({"role": "user", "content": prompt})
            response = self._call_llm(messages)
            
            # Update episode focus if we found strong evidence
            if passages and passages[0]["score"] > 0.6:
                state.current_episode_focus = passages[0]["episode_id"]

        # 3. Update State
        state.add_message("user", question)
        state.add_message("assistant", response)
        
        return response
