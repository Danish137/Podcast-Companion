# Development and Context Continuity Protocol

## Purpose

Prevent context loss, hallucinated progress, accidental scope changes, and inconsistent implementation when moving between Antigravity, Cursor, Codex, or another coding environment.

## Single source of truth

Chat history is not project state.

The repository documentation is project state.

The most important files are:

1. `AGENTS.md` - behavioral contract;
2. `STATUS.md` - current state;
3. `DECISIONS.md` - decision history;
4. `PROJECT_SPEC.md` - assignment/product requirements;
5. `ARCHITECTURE.md` - technical design;
6. `EVALUATION.md` - evaluation contract;
7. `IMPLEMENTATION_PLAN.md` - execution sequence.

## Session start protocol

Every coding-agent session must begin by reading:

```text
AGENTS.md
STATUS.md
DECISIONS.md
PROJECT_SPEC.md
```

Then read only the additional documents relevant to the current task.

After reading them, inspect the actual repository.

The agent must not claim that a feature exists because a document says it should exist.

Documents describe intent/status; source code and executed checks establish reality.

## Session end protocol

Before ending a meaningful session:

1. update `STATUS.md`;
2. update `DECISIONS.md` if a decision changed;
3. record tests/checks actually executed;
4. record failures;
5. record exact next action;
6. record any new unknowns.

## Change protocol

For each significant implementation:

1. state the intended behavior;
2. identify files likely to change;
3. inspect them;
4. implement the smallest change;
5. run relevant checks;
6. inspect output;
7. update status.

## Anti-hallucination rules

The agent must never:

- say "done" without verification;
- say "tests pass" without running them;
- infer that an API works because credentials exist;
- invent transcript content;
- invent episode metadata;
- invent evaluation results;
- invent source timestamps;
- claim grounding without inspecting evidence;
- silently replace an unavailable component with a mock in a final feature;
- silently change requirements.

If a component is mocked for development, label it clearly as a mock.

## Context handoff

When switching IDEs, the new agent should be given this instruction:

"Treat the repository documentation as the current project memory. Read AGENTS.md and STATUS.md first, then inspect the code. Do not rely on previous chat context."

## Working-state labels

Use these labels in `STATUS.md`:

- `NOT_STARTED`
- `IN_PROGRESS`
- `BLOCKED`
- `VERIFIED`
- `PARTIALLY_VERIFIED`
- `DEFERRED`
- `FAILED`

Do not mark a feature `VERIFIED` unless it was actually exercised.

## Scope control

If the agent proposes a feature not required by the product spec:

- explain why it is needed;
- estimate its cost;
- identify what it displaces;
- do not implement it automatically.

## Secrets

Never write API keys into markdown, source code, logs, screenshots, evaluation artifacts, or git history.

Use environment variables or the project's secret mechanism.

## Evidence discipline

When debugging:

`Observed behavior -> evidence -> hypothesis -> change -> verification`

Do not skip directly from symptom to rewrite.

## Evaluation discipline

The evaluation set is immutable once baseline evaluation starts, except for corrections to genuine case-definition errors. Any such correction must be documented.

The same cases must be used for baseline and improved evaluation.

## Cross-IDE compatibility

Use plain Markdown and ordinary repository files as the authoritative context.

IDE-specific instruction files may reference these documents, but must not become a second source of truth.
