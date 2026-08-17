"""
Fermi Companion - Evaluation Framework
Runs baseline and final evaluations across required cases.
"""

import json
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

from src.companion import FermiCompanion, ConversationState
from src.config import EVAL_DIR
from rich.console import Console
from rich.table import Table

console = Console()

# The 10 required evaluation cases covering different intents and behaviors
EVAL_CASES = [
    {
        "id": "C01",
        "type": "factual",
        "intent": "EXPLAIN",
        "question": "What is the core idea of special relativity?",
        "expected_behavior": "Provides a grounded explanation of relativity (c is constant, simultaneity is relative) citing ep01."
    },
    {
        "id": "C02",
        "type": "factual",
        "intent": "EXPLAIN",
        "question": "How do black holes radiate according to Hawking?",
        "expected_behavior": "Explains Hawking radiation citing ep02."
    },
    {
        "id": "C03",
        "type": "discovery",
        "intent": "DISCOVER",
        "question": "Which episodes should I listen to if I'm interested in biology and evolution?",
        "expected_behavior": "Recommends ep03 (Watson/Crick), ep08 (Darwin/Wallace), and ep13 (Meselson-Stahl)."
    },
    {
        "id": "C04",
        "type": "discovery",
        "intent": "DISCOVER",
        "question": "Are there any papers from before 1900?",
        "expected_behavior": "Recommends Darwin (1858) and Mendeleev (1869)."
    },
    {
        "id": "C05",
        "type": "comparison",
        "intent": "COMPARE",
        "question": "How do the ideas of information in Shannon's paper compare to the physical reality described by Einstein?",
        "expected_behavior": "Synthesizes concepts from both ep04 (Shannon) and ep01/06 (Einstein) with separate citations."
    },
    {
        "id": "C06",
        "type": "comparison",
        "intent": "COMPARE",
        "question": "What is the difference between how Darwin viewed change over time versus how Planck viewed energy?",
        "expected_behavior": "Synthesizes continuous evolution (ep08) vs discrete quanta (ep11)."
    },
    {
        "id": "C07",
        "type": "follow_up",
        "intent": "EXPLAIN",
        "question": "I don't understand the train example.",
        "pre_context": [
            {"role": "user", "content": "Explain special relativity."},
            {"role": "assistant", "content": "Special relativity says the speed of light is constant. Einstein used thought experiments with trains to explain this. [ep01, 15:00]"}
        ],
        "expected_behavior": "Understands 'train example' refers to relativity and uses previous/new context to explain the thought experiment."
    },
    {
        "id": "C08",
        "type": "follow_up",
        "intent": "EXPLAIN",
        "question": "What does 'discrete' mean in that context?",
        "pre_context": [
            {"role": "user", "content": "What did Planck propose?"},
            {"role": "assistant", "content": "Planck proposed that energy is not continuous, but comes in discrete packets called quanta. [ep11, 20:00]"}
        ],
        "expected_behavior": "Understands 'discrete' refers to energy quanta from the previous turn."
    },
    {
        "id": "C09",
        "type": "unsupported",
        "intent": "UNSUPPORTED",
        "question": "Explain string theory and how many dimensions it requires.",
        "expected_behavior": "Politely refuses to answer, explicitly stating there is not enough evidence in the supplied episodes."
    },
    {
        "id": "C10",
        "type": "unsupported",
        "intent": "UNSUPPORTED",
        "question": "Who won the World Series in 2024?",
        "expected_behavior": "Politely refuses, explicitly stating the podcast collection does not cover this."
    },
    {
        "id": "C11",
        "type": "conversational_reference",
        "intent": "EXPLAIN",
        "question": "Where do they talk about it?",
        "pre_context": [
            {"role": "user", "content": "What covers information theory?"},
            {"role": "assistant", "content": "The podcast catalogue includes the following episode covering information theory:\n- Shannon and the Birth of Information, 1948"}
        ],
        "expected_behavior": "Resolve 'it' to information theory and retrieve the Shannon episode."
    },
    {
        "id": "C12",
        "type": "conversational_timestamp",
        "intent": "EXPLAIN",
        "question": "Show me exactly where they discuss it.",
        "pre_context": [
            {"role": "user", "content": "What covers information theory?"},
            {"role": "assistant", "content": "The podcast catalogue includes the following episode covering information theory:\n- Shannon and the Birth of Information, 1948"}
        ],
        "expected_behavior": "Return relevant Shannon transcript evidence and accurate timestamp(s)."
    },
    {
        "id": "C13",
        "type": "conversational_source",
        "intent": "EXPLAIN",
        "question": "Can you give me the part where they explain channel capacity?",
        "pre_context": [
            {"role": "user", "content": "Which episode explains Shannon's work?"},
            {"role": "assistant", "content": "The episode covering Shannon's work is 'Shannon and the Birth of Information, 1948'."}
        ],
        "expected_behavior": "Retrieve the correct Shannon episode and timestamp."
    },
    {
        "id": "C14",
        "type": "context_switch",
        "intent": "EXPLAIN",
        "question": "What about special relativity?",
        "pre_context": [
            {"role": "user", "content": "What covers information theory?"},
            {"role": "assistant", "content": "The podcast catalogue includes the following episode covering information theory:\n- Shannon and the Birth of Information, 1948"}
        ],
        "expected_behavior": "Correctly switch topic rather than remaining locked to Shannon."
    },
    {
        "id": "C15",
        "type": "contextual_explanation",
        "intent": "EXPLAIN",
        "question": "What does 'discrete' mean in that context?",
        "pre_context": [
            {"role": "user", "content": "Explain Planck's quantum idea."},
            {"role": "assistant", "content": "Planck proposed that energy is not continuous, but comes in discrete packets called quanta. [Max Planck and the Quantum Hypothesis, 14:00]"}
        ],
        "expected_behavior": "Resolve 'that context' to Planck's quantum discussion and answer using the relevant source evidence."
    }
]


def run_evaluation(run_name: str):
    """Run all evaluation cases and save results."""
    console.print(f"\\n[bold blue]Starting Evaluation Run: {run_name}[/bold blue]\\n")
    
    companion = FermiCompanion()
    results = []
    
    for case in EVAL_CASES:
        console.print(f"Running Case {case['id']} ({case['type']})...")
        
        state = ConversationState()
        if "pre_context" in case:
            state.history = case["pre_context"].copy()
            # We don't have perfect last_retrieved_evidence here, but the router should handle it
            
        start_time = datetime.now()
        
        try:
            intent = companion.route_intent(case["question"], state)
            response = companion.process_message(case["question"], state)
            
            # Extract citations for logging
            import re
            citations = re.findall(r'\[(.*?)\]', response)
            
            # Grab evidence text for logging
            evidence_text = []
            retrieved_chunk_ids = []
            if getattr(state, 'last_retrieved_evidence', None):
                for p in state.last_retrieved_evidence:
                    evidence_text.append(p.get("text", ""))
                    if "chunk_id" in p:
                        retrieved_chunk_ids.append(p["chunk_id"])
                        
            # Get the rewrite if it exists
            resolved_query = getattr(state, 'last_resolved_query', case["question"])
            
            result = {
                "case_id": case["id"],
                "conversation_history": case.get("pre_context", []),
                "question": case["question"],
                "resolved_query": resolved_query,
                "detected_intent": intent,
                "expected_intent": case["intent"],
                "selected_episode_focus": getattr(state, 'current_episode_focus', None),
                "retrieved_chunk_ids": retrieved_chunk_ids,
                "evidence_text": evidence_text,
                "response": response,
                "citations": citations,
                "evidence_retrieved_count": len(state.last_retrieved_evidence) if hasattr(state, 'last_retrieved_evidence') else 0,
                "status": "success",
                "time_ms": int((datetime.now() - start_time).total_seconds() * 1000)
            }
            
            console.print(f"  [green]OK {intent} | {len(citations)} citations[/green]")
            
        except Exception as e:
            console.print(f"  [red]ERR Error: {str(e)}[/red]")
            result = {
                "case_id": case["id"],
                "question": case["question"],
                "status": "error",
                "error": str(e)
            }
            
        results.append(result)
        
    # Save raw results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = EVAL_DIR / "results" / f"eval_{run_name}_{timestamp}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    console.print(f"\\n[bold green]Evaluation complete. Results saved to {output_path}[/bold green]")
    
    # Print summary table
    table = Table(title=f"Evaluation Summary: {run_name}")
    table.add_column("Case", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Intent Match", justify="center")
    table.add_column("Citations", justify="right")
    table.add_column("Status")
    
    for i, r in enumerate(results):
        case = EVAL_CASES[i]
        intent_match = "OK" if r.get("detected_intent") == case["intent"] else f"ERR ({r.get('detected_intent')})"
        citations = str(len(r.get("citations", [])))
        status = "[green]OK[/green]" if r.get("status") == "success" else "[red]ERR[/red]"
        
        table.add_row(case["id"], case["type"], intent_match, citations, status)
        
    console.print(table)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="baseline", help="Name of the evaluation run (e.g., baseline, improved)")
    args = parser.parse_args()
    
    run_evaluation(args.name)


if __name__ == "__main__":
    main()
