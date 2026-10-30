# State Memory Reference

## Primary Policy Ownership

This skill owns durable auto-memory read gates, write gates, schema, cleanup boundaries, and reconciliation with local artifacts.

## State Layer Separation

- Local artifacts (repo files, code, docs) own current implementation state.
- Project `AGENTS.md` owns durable repo guidance.
- `handoff.md` owns compact restart state.
- Active plans own detailed decisions, acceptance, research, and verification.
- `~/.claude/projects/<project-slug>/memory/*.md` + `MEMORY.md` own concise durable recall hints only — facts the repository itself does not record (user preferences, feedback, project context, external references).

Memory is not source of truth for implementation state. A memory file's own header warns it is a point-in-time snapshot — treat a code/file:line claim in it as a hint until reconciled against the current repo.

In a full state-save sweep, do not write memory until canonical local state (`handoff.md`, `AGENTS.md`) is current. The sweep and the meaning of "current" are defined by `claude-project-state` (SKILL.md step 9), which is the single owner of that sequence.

## Read Gate

Use memory only when historical context can materially change the decision:

- durable user preference or working-style feedback;
- accepted project decision;
- reusable pattern;
- known error or pitfall;
- runtime-stable fact;
- pointer to an external system (reference-type memory).

Skip memory for:

- clear local edits;
- current plan status;
- verification logs;
- next actions;
- raw conversation summaries;
- external version facts (verify those against current authoritative sources instead).

Retrieval rules:

1. `MEMORY.md` is already loaded into context every session — start there, it costs nothing extra.
2. Only `Read` an individual memory file when the one-line index entry is not enough detail.
3. Reconcile accepted findings against the current repo, `handoff.md`, active plans, or `git log`/`git blame` before using them — "the memory says X exists" is not "X exists now."
4. Drop foreign-project, duplicate, verbose, routine-checkpoint, vague, or raw-summary candidates before they ever become a memory file.

Time-only recall ("what were we doing last week") is answered from `handoff.md` and session context first; memory files are for durable facts, not a session timeline.

## Write Gate

Write (create or update a memory file + its `MEMORY.md` line) only when all are true:

- content is durable beyond this session and this project's current state;
- content is not already owned by `AGENTS.md`, `handoff.md`, active plans, docs, or code — per the global auto-memory rule, save to memory only facts the repository does not record;
- content is non-duplicate of an existing memory file (check `MEMORY.md` first; update that file in place instead of creating a near-duplicate);
- content is not sensitive (no secrets, credentials, private endpoints, customer data);
- the user asked to remember it, or it clearly matches one of the four memory types (user / feedback / project / reference) as defined in the global system prompt.

Reject:

- routine checkpoints, plan phase status, fix status, verification logs, next actions, project-local todos — those belong in `handoff.md` via `session-handoff`;
- raw summaries or transcript dumps;
- code patterns, conventions, architecture, or file paths derivable by reading the current repo;
- git history or who-changed-what (`git log`/`git blame` are authoritative);
- debugging solutions or fix recipes (the fix is in the code; the commit message has the context).

## Write Semantics

Memory files may be edited or deleted directly: the global auto-memory instructions say to update or remove a memory once it is confirmed wrong, stale, or superseded by new repo state, and to remove an entry outright when the user asks to forget something. Prefer updating the existing file over creating a new "supersedes" entry, since there is no cross-reference mechanism enforcing that chain here — just keep the file's own content and `description` current, and update the `MEMORY.md` line to match.

Only the main agent writes memory files. A helper/sub-agent that surfaces a memory-worthy fact returns it to the main agent to gate and write — do not let a sub-agent write directly into `~/.claude/projects/<project-slug>/memory/`.

## Required Memory Shape

Use `memory-schema.md` when writing, auditing, or validating a memory entry's frontmatter and type.

## Cleanup Boundary

Memory cleanup (merging duplicates, pruning the `MEMORY.md` index, fixing stale facts) is itself covered by the `anthropic-skills:consolidate-memory` skill when it is available in the session's skill list — prefer that for a dedicated cleanup pass. When doing ad-hoc cleanup here, state which files are being merged/removed before editing them; this is a local file edit like any other, not a separate approval-gated tool call.
