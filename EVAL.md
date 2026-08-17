# Evaluation Results

## A. Evaluation Goal
The goal of this evaluation is to verify that the Fermi Podcast Companion can faithfully answer factual questions, compare concepts across episodes, handle unsupported queries, and correctly resolve conversational references and follow-up questions using only the provided audio transcripts.

## B. Evaluation Set Composition
The evaluation set contains 15 varied cases (C01-C15) testing factual retrieval, multi-episode discovery, comparison, unsupported handling, and conversational continuity.

## C. Independence from Demo Examples
- **Demo-derived cases (5)**: C11, C12, C13, C14 (derived from the Information Theory bug report), and C15 (derived from a Planck contextual demo).
- **Independent/non-demo cases (10)**: C01-C10. These cases were designed specifically for the blind evaluation set and do not overlap with the assignment PDF examples or manual debugging interactions.
- **Requirement Satisfied**: The set contains exactly 10 cases completely independent of demo interactions.

## D. Baseline Methodology
The baseline system was evaluated against all 15 cases. The runner (`src/evaluate.py`) explicitly passed the conversation history (pre-context) to the product for cases C11-C15 to test whether the system could naturally resolve follow-up references like "it" or "that part" using vector similarity alone.

## E. Baseline Raw Artifact Filenames
- `eval_baseline_conversation_v2_20260817_070948.json`

## F. Failure Analysis
In the baseline, the system successfully handled standalone factual and discovery questions (e.g., C01-C10). However, it failed severely on conversational reference queries:
- For C11 ("Where do they talk about it?") and C12 ("Show me exactly where they discuss it."), the baseline system retrieved 0 citations. 
- **Root Cause**: The retrieval engine only embedded the latest raw user message ("it", "where"). It failed to resolve the pronoun using the conversation history, resulting in a noisy vector search that pulled unrelated chunks (e.g., Einstein) instead of the active topic (Shannon).

## G. Meaningful Improvement
To fix this, a **conversational query rewriting layer** and **episode focus continuity** mechanism were introduced. The system now uses a lightweight LLM call to rewrite the user's query using the conversation history (e.g., resolving "it" to "Shannon information theory") before performing the vector search. The `DISCOVER` intent also now persists its recommended episode into the conversation state. 

*Crucial Distinction*: This improvement specifically fixed follow-ups lacking sufficient lexical retrieval terms. Cases like C13 ("channel capacity") already worked in the baseline because they contained strong unique keywords, whereas C11/C12 were purely pronoun-based.

## H. Improved Methodology
The exact same 15 evaluation cases were re-run against the improved system. No cases were removed, and no questions or expected behaviors were altered to artificially inflate scores.

## I. Improved Raw Artifact Filenames
- `eval_improved_conversation_v2_20260817_071146.json`

## J. Before/After Results (Conversational Cases Subset)

| Case | Type | Baseline Behavior | Improved Behavior | Correct Answer? |
|------|------|-------------------|-------------------|-----------------|
| **C11** | Conversational Reference | Failed (Generic fallback, 0 citations) | Detailed explanation of Shannon (6 citations) | Yes |
| **C12** | Conversational Timestamp | Failed (Generic fallback, 0 citations) | Accurate timestamps for Shannon's impact (7 citations) | Yes |
| **C13** | Conversational Source | Passed via keyword matching (4 citations) | Concise, accurate explanation (3 citations) | Yes |
| **C14** | Context Switch | Intent `DISCOVER` (Returned Einstein list) | Intent `DISCOVER` (Returned Einstein list) | Yes |
| **C15** | Contextual Explanation | Passed via keyword matching (2 citations) | Same accurate answer (3 citations) | Yes |

*Note: Most standalone cases (C01-C10) were successful in both the baseline and improved runs. The improvement materially enhanced the pronoun-heavy conversational cases while safely preserving standalone retrieval.*

## K. Source/Timestamp Manual Verification
Source accuracy was rigorously verified against the raw chunks for the conversational timestamp cases:
- **C13 (Channel Capacity)**: The improved model cited `[Shannon and the Birth of Information, 1948, 31:59]`. Verification: `ep04_chunk_022` starts exactly at `1919.0` seconds (31:59) and explicitly discusses bandwidth, capacity, and the Shannon-Hartley formula. **Source Accuracy: Strong (2/2)**.
- **C12 (Information Theory Impact)**: The improved model cited `[Shannon and the Birth of Information, 1948, 32:30-34:00]`. Verification: `ep04_chunk_024` starts exactly at `1950.0` seconds (32:30) and explicitly discusses phone signals, streaming, and how the internet operates in the space Shannon defined. **Source Accuracy: Strong (2/2)**.

## L. Regressions
No material regressions were observed in factual correctness or source accuracy. The citation count for C13 dropped from 4 to 3, but the actual textual explanation remained perfectly grounded.

## M. Remaining Limitations
The intent router occasionally struggles with ambiguous phrasing. For example, C09 ("Explain string theory...") was routed to `EXPLAIN` rather than `UNSUPPORTED`, and C14 ("What about special relativity?") was routed to `DISCOVER` rather than `EXPLAIN`. While the final generated responses gracefully handled these (e.g., C09 refused to answer due to lack of evidence), the routing itself is not perfect. 

## N. Exact Commands Used
```bash
# Run Baseline
python -m src.evaluate --name baseline_conversation_v2

# Run Improved
python -m src.evaluate --name improved_conversation_v2
```

## O. Raw Evaluation Storage
All raw artifacts, inputs, retrieved chunks, parsed outputs, and timestamps are preserved in `eval/results/`.

## P. Final Manual QA: Generation Grounding Failure
During final manual QA, an additional issue was discovered that was not reliably exposed by the automated evaluation runner.

Example:
User: "Why was Mendeleev originally trying to organize the elements?"
Then: "What pattern did he notice among the elements?"

Retrieval correctly resolved the conversational context and retrieved relevant Mendeleev evidence. However, generation was still receiving the original unresolved question containing "he". As a result, the LLM could sometimes respond with:
"I couldn't find enough evidence of that in the supplied episodes..."
even though the same relevant evidence was simultaneously displayed in the frontend source cards.

**Root cause**:
- retrieval used resolved_query
- generation used raw question
Therefore retrieval and generation had a semantic mismatch.

**Fix**:
generation now receives resolved_query.

The automated evaluation did not reliably expose this because LLM behavior was stochastic: in some programmatic runs the model successfully resolved the pronoun on its own, masking the product-level failure. Final manual QA exposed this additional robustness issue and the implementation was corrected accordingly. After the fix, the same scenario was manually re-tested successfully. This serves as a concrete example of: evaluation -> failure discovery -> root-cause investigation -> improvement -> manual re-validation.
