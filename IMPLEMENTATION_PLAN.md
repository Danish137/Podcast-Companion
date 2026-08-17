# Two-Day Implementation Plan

## Guiding rule

Get a complete vertical slice working before adding sophistication.

## Phase 0 - Repository audit

Goal:

Understand the workspace and establish the actual starting state.

Tasks:

- inspect repository;
- inspect supplied audio;
- identify runtime/tooling;
- identify existing files;
- verify available OpenRouter configuration without exposing secrets;
- document actual corpus size and formats;
- identify unknowns.

Deliverable:

Updated `STATUS.md`.

## Phase 1 - Ingestion

Goal:

Turn raw audio into timestamped source material.

Tasks:

- transcription from supplied audio;
- normalize transcript format;
- preserve start/end timestamps;
- create episode manifest;
- verify a sample manually.

Acceptance:

At least one complete episode can be traced:

`audio -> transcript -> timestamped segment`.

## Phase 2 - Retrieval foundation

Goal:

Make source evidence retrievable.

Tasks:

- segment transcripts;
- create episode metadata;
- create passage representations/index;
- implement episode-level and passage-level retrieval where justified;
- preserve provenance.

Acceptance:

Given known questions, the system can retrieve supporting source regions.

## Phase 3 - Minimal end-to-end product

Goal:

A learner can ask a question and receive an answer with source evidence.

Flow:

`question -> retrieval -> answer -> evidence/timestamp`.

Acceptance:

A human can use the product for supported questions.

## Phase 4 - Product behaviors

Implement in this order:

1. conversational follow-up;
2. explanation adaptation;
3. unsupported handling;
4. episode discovery;
5. cross-episode comparison.

Do not add optional features before these work.

## Phase 5 - Evaluation baseline

Create the evaluation set.

Run baseline.

Preserve raw outputs.

Manually inspect failures.

## Phase 6 - Evidence-driven improvement

Implement one meaningful improvement based on baseline failures.

Preferred candidate:

- stronger episode-aware retrieval;
- reranking;
- evidence-aware answer generation;
- grounding verification.

Choose based on actual evidence.

## Phase 7 - Re-evaluation

Run the same cases.

Generate comparison results.

Record regressions and unresolved issues.

## Phase 8 - Demo and documentation

Complete:

- README;
- PRODUCT.md;
- EVAL.md;
- STATUS.md;
- DECISIONS.md;
- demo flow.

## Time allocation principle

Approximate priority:

- 30% complete product;
- 25% evaluation and improvement;
- 20% ingestion/retrieval;
- 15% trust/source UX;
- 10% polish.

Do not spend most of the time on frontend styling.
