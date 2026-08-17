# Evaluation Plan

## Purpose

Evaluation is a first-class part of the product.

The goal is not to produce an impressive aggregate score. The goal is to determine whether the system gives learners useful, faithful, verifiable answers and to identify where it fails.

The assignment requires:

- at least 10 varied cases beyond demo examples;
- a repeatable runner;
- preservation of raw inputs and outputs;
- baseline evaluation;
- manual inspection;
- one meaningful improvement;
- rerun of the same cases;
- documented improvement/regression/unresolved issues.

## Evaluation set

Target 15 cases.

| Category | Target |
|---|---:|
| Direct factual/source questions | 3 |
| Conceptual explanation | 2 |
| Conversational follow-up | 2 |
| Cross-episode comparison | 2 |
| Episode discovery | 2 |
| Source/timestamp lookup | 1 |
| Unsupported requests | 2 |
| Misleading/false-premise request | 1 |
| Total | 15 |

The exact questions must be derived from the actual supplied podcast corpus after ingestion. Do not invent expected answers without checking the source.

## Case schema

Each evaluation case should conceptually contain:

```text
case_id
category
user_query
conversation_context (optional)
expected_behavior
expected_episode(s) (when applicable)
expected_source_region(s) (when known)
notes
```

## Metrics

### 1. Answer correctness

Does the answer correctly address the question?

### 2. Groundedness

Are substantive claims supported by supplied podcast evidence?

### 3. Source accuracy

Do the episode and timestamp actually support the answer?

### 4. Evidence retrieval

Was the relevant evidence retrieved?

### 5. Unsupported handling

When the corpus lacks evidence, does the system abstain/qualify instead of hallucinating?

### 6. Conversation usefulness

For follow-ups, does the system correctly understand the previous context and provide a useful continuation?

### 7. Cross-episode completeness

For comparison questions, does the response represent the relevant episodes rather than relying on only one?

## Scoring

Use a simple, inspectable scale such as 0-2 per dimension:

- 0 = failed
- 1 = partially correct / materially imperfect
- 2 = strong

Do not optimize the metric merely to improve the reported score.

## Baseline

The first baseline should be intentionally simple.

Example:

`query -> semantic retrieval -> top-k evidence -> answer generation -> sources`

Run the full evaluation set and preserve raw results before making the major improvement.

## Manual failure analysis

For every significant failure, record:

- case;
- actual output;
- retrieved evidence;
- expected behavior;
- failure type;
- likely cause;
- severity;
- proposed fix.

## Meaningful improvement

Preferred improvement direction:

Evidence-aware / episode-aware retrieval plus stronger grounding verification.

Only implement this if baseline failures support it.

The improvement must be justified by observed failures.

## Before/after comparison

Rerun exactly the same cases.

Report:

- metric before;
- metric after;
- absolute change;
- examples of improvement;
- regressions;
- unresolved failures.

## Raw evidence

Preserve:

- evaluation input;
- retrieved evidence;
- raw model output;
- parsed/structured result;
- final score/judgment.

Do not only save aggregate metrics.

## Evaluation integrity

Never:

- change evaluation questions to make the improvement look better;
- remove failed cases;
- tune expected answers to the model output;
- claim a check passed without running it.

If a metric is LLM-judged, document the judge prompt/model and treat it as evidence rather than unquestionable ground truth.
