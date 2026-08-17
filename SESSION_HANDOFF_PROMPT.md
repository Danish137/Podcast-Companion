# Cross-IDE Session Handoff Prompt

Use this whenever opening the project in a new IDE/agent or after a long context break.

You are continuing an existing Fermi Podcast Companion project.

Do not rely on previous chat history.

Read:

1. AGENTS.md
2. STATUS.md
3. DECISIONS.md
4. PROJECT_SPEC.md
5. ARCHITECTURE.md
6. EVALUATION.md
7. the relevant implementation files

Then inspect the repository and verify that the documented state matches reality.

Report:

- current phase;
- what is actually implemented;
- what is actually verified;
- what remains;
- current blockers;
- important recent decisions;
- the smallest next task that advances the project toward submission.

Do not change code during this audit.

If STATUS.md conflicts with the repository, trust the repository's observed state and correct STATUS.md.

If a requirement is ambiguous, identify it as an unknown rather than guessing.

Only after the audit should implementation begin.
