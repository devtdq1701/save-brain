---
name: claude-state-memory
description: "Use this skill when a task needs durable auto-memory lookup or write decisions, cross-session recall, durable preference/decision/pattern retrieval, memory audit, or separation between memory and local state. Triggers: remember this, do you recall, what did we decide before, search memory, memory audit, nho cai nay, truoc day da quyet gi. Do not use for clear local edits, current plan status, handoff-only updates, AGENTS.md routing without memory impact, external version facts, or routine checkpoints. Output: memory gate decision, accepted recall, target state surface, persistence decision, and verification."
---

# Claude State Memory

## Purpose

Own exactly one reusable workflow:

- Job: decide when to read or write Claude's durable auto-memory, and keep it separate from local work state.
- Primary surfaces: context recovery, status recall, full state-save sweeps, unclear continuation, durable recall, and memory hygiene.
- Non-goals: general AGENTS/handoff routing, external version facts, procedure extraction, or routine checkpoint storage.

## What "memory" means here

Claude has no MCP memory tool in this environment. Durable recall is a plain file system under
`~/.claude/projects/<project-slug>/memory/`: one Markdown file per memory plus an index `MEMORY.md`
(always loaded into context). This skill gates reads and writes on those files via `Read`/`Write`/`Edit`.

## Use When

- The user asks to recall prior preferences, decisions, patterns, known pitfalls, or what should be remembered.
- Historical context may change scope, implementation, verification, or risk handling.
- A task needs a memory read/write decision or a memory audit (duplicates, stale facts, bloated index).
- A full state-save sweep needs a strict persistence gate after canonical local state (`handoff.md`, `AGENTS.md`) is current.
- The user explicitly asks to remember or forget something (save immediately per the auto-memory system prompt; this skill's gate still applies to judge type and avoid duplication).

## Skip When

- Local files (repo code, docs, `AGENTS.md`) already provide the source of truth for a clear edit — per the auto-memory rule, save to memory only facts the repository does not record.
- The content is current plan status, verification log, next action, or handoff-only state — that belongs in `handoff.md` via `session-handoff`.
- The information is current external behavior; use official docs or primary sources, not memory.
- The task is AGENTS versus handoff routing with no memory impact.

## Inputs

- Required: memory intent, current project (the session's working directory / project slug), and the decision the memory could change.
- Optional: active plan, handoff path, candidate memory text, existing `MEMORY.md` contents.
- Reference files: `references/policy-guide.md`, `references/memory-schema.md`.

## Workflow

1. State whether the memory gate is used or skipped, and why.
2. If reading: `MEMORY.md` is already in context (it's auto-loaded); for depth, `Read` the specific memory file it points to. Search narrowly by project and topic; accept only relevant findings. A memory file's header already warns it is a point-in-time snapshot — verify any code/file:line claim against the current repo before asserting it as fact (see `references/policy-guide.md`).
3. Reconcile accepted recall against local source-of-truth artifacts (repo files, `AGENTS.md`, git log) before using it; prefer what you observe now over a stale memory.
4. In a full state-save sweep this skill is mandatory even when the answer is "do not store memory." The sweep is defined by `claude-project-state` (step 9); do not restate its steps here. Only requirement from this side: canonical local state (`handoff.md`/`AGENTS.md`) must already be written and validated before any memory write is considered.
5. If writing: apply the durability, ownership, sensitivity, duplicate, and type gates in `references/memory-schema.md`. Check `MEMORY.md` for an existing entry on the same topic first — update that file in place rather than creating a near-duplicate.
6. For recap/context-recovery, read `MEMORY.md` first (cheap, already-loaded); only open individual memory files when the index line is not enough.
7. Report the accepted recall or persistence decision with verification and residual risk. `accepted` means the gate passed; `stored` means the `Write`/`Edit` call to the memory file (and the matching `MEMORY.md` index line) actually completed — report file paths for both.

## Progressive Disclosure

- Read `references/policy-guide.md` before any memory read/write decision or cleanup discussion.
- Read `references/memory-schema.md` only when writing, auditing, or validating a memory entry's frontmatter/type.
- No script validates memory files; `~/.claude/scripts/claude_save_brain.py` covers only `handoff.md`/`AGENTS.md`. Every gate in `references/memory-schema.md` is a judgment check this skill applies itself — state explicitly which gate rejected a candidate and why.

## Output Contract

Return:

- memory gate decision;
- accepted recall and rejected/noisy recall summary;
- target state surface (which memory file, or "no memory needed");
- persistence decision and the file(s) written;
- verification or skipped-check reason.

Do not return:

- raw memory-file dumps beyond what's needed to answer;
- secrets, private endpoints, or sensitive payloads;
- routine checkpoint or plan-status content (that belongs in `handoff.md`).
