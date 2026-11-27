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
generation now receives resolved_query. (Later refined in section Q: generation receives the learner's original message plus the resolved query as context, so "I didn't get it" is answered as a request to re-explain rather than as the rewritten question.)

The automated evaluation did not reliably expose this because LLM behavior was stochastic: in some programmatic runs the model successfully resolved the pronoun on its own, masking the product-level failure. Final manual QA exposed this additional robustness issue and the implementation was corrected accordingly. After the fix, the same scenario was manually re-tested successfully. This serves as a concrete example of: evaluation -> failure discovery -> root-cause investigation -> improvement -> manual re-validation.

## Q. Second Improvement Round: Adversarial Multi-Turn Probing

The 15-case suite passed, but it scores each case in isolation. To find failures a real learner would hit, 16 adversarial turns in 6 multi-turn conversations were run against the live API: re-explanation requests, false premises, discover→follow-up, greetings, prompt injection, topic switches and comparisons.

**Raw artifacts** (question, intent, full answer and returned sources per turn):
- `probe_adversarial_before_20261127.json`: before the fixes
- `probe_adversarial_after_20261127.json`: after the fixes, all 16 turns
- `probe_adversarial_after_final_20261127.json`: after the final prompt adjustments (targeted conversations)

**Failures observed and fixes:**

| Turn | Before | Root cause | After |
|------|--------|------------|-------|
| "Which episodes cover biology?" after a relativity question | 5 relativity sources shown under a biology answer | Evidence state not reset on `DISCOVER` turns | 0 sources (evidence is reset every turn) |
| "Tell me more about the second one" (after the biology list) | Refusal | `DISCOVER` locked episode focus to the *first* listed episode | Grounded answer about Darwin & Wallace (3 cited sources) |
| "How does that relate to Shannon's idea of entropy?" (after attention) | Answer linked Shannon to *black-hole* entropy | `COMPARE` did not resolve "that"; retrieved the wrong episodes | Retrieves Shannon + Attention, explains each with citations, and states the episodes don't connect them |
| "I did not get it clearly" | Near-verbatim repeat of the previous answer | Generation only saw the rewritten question | Shorter re-explanation with an everyday analogy, still cited |
| "hi" | "I couldn't find enough evidence…" | No greeting intent | Short description of what the companion can do |
| Compare / explain answers | 5–9 source cards, many never cited | All retrieved passages were shown | Only passages the answer cites (matched by episode + timestamp) |
| Partial refusal ("not in that episode, but Bell's Theorem says…") | Real citations hidden | Sources were suppressed whenever the refusal phrase appeared | Cited sources shown |

Behaviour that was already correct and stayed correct: "Who are the hosts?" and "What did the hosts say about the Higgs boson?" are refused (the transcripts contain neither), and prompt injection is refused.

**Regression check on the 15-case suite:** the same cases were re-run before and after.

| Run | Artifact | Intent match | Status |
|-----|----------|--------------|--------|
| Before | `eval_pre_session4_20261127_143540.json` | 13/15 | 15/15 ran |
| After | `eval_post_session4_20261127_143955.json` | 13/15 | 15/15 ran |
| After (final prompts) | `eval_post_session4_final_20261127_144543.json` | 13/15 | 15/15 ran |

The same two routing mismatches as in section M remain (C09 routed `EXPLAIN` but still refuses; C14 routed `DISCOVER` but still switches topic correctly). No case regressed. The runner now records the intent the companion actually used (previously a second, separate router call) and the cited sources per case.

**Remaining limitation:** when re-explaining with an analogy, the model sometimes attaches a citation to the analogy sentence itself. Analogies are allowed as teaching aids, but only claims about episode content are meant to be cited.
