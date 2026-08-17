# Fermi Companion - AI Coding Agent Contract

## Mission

Build the Fermi Podcast Companion as a complete, runnable learner product from the supplied raw podcast audio.

The product is NOT "a RAG chatbot". RAG/retrieval is an implementation mechanism. The product is a grounded learning companion that helps a learner:

1. understand difficult concepts from the supplied episodes,
2. ask natural follow-up questions,
3. discover which episodes/parts are useful,
4. compare concepts across episodes,
5. verify answers against timestamped source audio,
6. handle unsupported questions honestly.

The primary success criterion is trustworthy usefulness, not UI polish.

## Source of truth

Before making decisions, read these project documents:

- `PROJECT_SPEC.md`
- `PRODUCT.md`
- `ARCHITECTURE.md`
- `EVALUATION.md`
- `IMPLEMENTATION_PLAN.md`
- `STATUS.md`
- `DECISIONS.md`
- `DEVELOPMENT_PROTOCOL.md`

The assignment brief is also a source of truth. Do not invent requirements that are not present in it.

## Non-negotiable assignment requirements

The system must:

- start from the supplied raw audio;
- not use YouTube/hosting-platform captions, transcripts, or caption/transcript APIs as input;
- provide a runnable conversational learner experience;
- remain faithful to the supplied audio;
- make substantive responses checkable against the source;
- do more than display a transcript or one-time summary;
- include a runnable evaluation system;
- include at least 10 varied evaluation cases beyond demo examples;
- preserve raw evaluation inputs and outputs;
- run an initial/baseline evaluation;
- manually inspect concrete successes/failures;
- make one meaningful improvement based on observed failures;
- rerun the same evaluation set;
- document results, failure analysis, and measured improvement;
- provide runnable source code, README/setup, product note, run artifacts or reproducible artifact creation, EVAL.md, and a short demo.

Non-goals include production infrastructure, authentication, billing, large continuously changing catalogue support, training a model from scratch, highly polished frontend, audio editing, podcast generation, and voice cloning.

## Coding-agent behavior

### Never guess when project evidence is available

Before changing code:

1. inspect the relevant existing files;
2. inspect `STATUS.md`;
3. inspect relevant decisions;
4. verify assumptions against the actual repository;
5. only then implement.

If something is unclear, mark it as `UNKNOWN` and investigate. Do not silently invent an answer.

### Never silently change product scope

If an implementation idea changes the intended user, core workflow, grounding policy, evaluation strategy, or architecture, stop and record the proposed change in `DECISIONS.md` before implementing it.

### Never treat generated text as evidence

LLM output is not source truth. Podcast-derived evidence is source truth.

Every factual answer about the supplied collection should be grounded in retrieved source evidence.

### Preserve provenance

Wherever transcript/source data is used, preserve enough metadata to identify:

- episode,
- source segment,
- start timestamp,
- end timestamp.

Do not discard timestamps during preprocessing.

### Do not optimize for architecture novelty

Prefer the simplest system that satisfies the product and evaluation requirements.

Do not introduce agents, knowledge graphs, fine-tuning, complex orchestration, or infrastructure merely to make the project look sophisticated.

### Evaluation is part of implementation

Do not leave evaluation until the end.

The evaluation runner and case set are first-class project artifacts.

Any meaningful retrieval/grounding change should be tested against the evaluation set.

### Protect working behavior

Before large refactors:

- run the existing relevant checks;
- understand what currently works;
- make small changes;
- rerun checks.

Do not rewrite functioning components merely because you prefer a different architecture.

## Context continuity protocol

At the end of every meaningful work session:

1. update `STATUS.md`;
2. record new architectural/product decisions in `DECISIONS.md`;
3. record unresolved issues in `STATUS.md`;
4. record commands/checks run and their outcomes;
5. record the exact next recommended task.

When starting a new session/IDE:

1. read `AGENTS.md`;
2. read `STATUS.md`;
3. read `DECISIONS.md`;
4. read the relevant implementation/product docs;
5. inspect the repository before acting.

Never infer progress from chat history alone.

## Definition of done

A feature is not "done" because code exists.

It is done only when:

- implementation exists;
- the intended behavior is clear;
- relevant checks/tests run;
- failures are understood;
- documentation/status is updated;
- the feature does not violate the product or grounding requirements.

## Response protocol for coding agents

Before implementation:
- summarize the current repository state;
- identify relevant requirements;
- identify assumptions/unknowns;
- propose the smallest next step.

After implementation:
- list changed files;
- explain behavior changes;
- report checks/tests and results;
- report known limitations;
- update project state files.

Do not claim a test passed unless it was actually run.
Do not claim a feature works unless it was actually verified.
