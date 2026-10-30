# Memory Schema

Use this only when writing, auditing, or validating a Claude auto-memory entry.

> **Source of truth:** the actual schema is defined in the global system prompt's "auto memory"
> section (loaded every session) — this page restates it for use inside this skill's gates. If the
> two ever disagree, the system prompt wins and this page is the bug. There is no validating script
> here (unlike `handoff.md`/`AGENTS.md`, which go through `~/.claude/scripts/claude_save_brain.py`):
> every check below is applied by the agent itself, not enforced in code.

## File Layout

- One file per memory under `~/.claude/projects/<project-slug>/memory/<kebab-case-name>.md`.
- One index line per memory in `~/.claude/projects/<project-slug>/memory/MEMORY.md` (always loaded into context; keep each line under ~150 characters).
- `MEMORY.md` itself has no frontmatter and holds no memory content directly — it is a pointer list only: `- [Title](file.md) — one-line hook`.

## Required Frontmatter (per memory file)

```markdown
---
name: {{short-kebab-case-slug}}
description: {{one-line summary, specific enough to judge future relevance}}
metadata:
  type: {{user, feedback, project, reference}}
---
```

## Type Tags (`metadata.type`)

- `user` — role, goals, responsibilities, knowledge of the person being worked with.
- `feedback` — corrections AND confirmations of how to approach work; body structure: the rule, then **Why:** and **How to apply:** lines.
- `project` — ongoing work, decisions, incidents not derivable from code/git; body structure: the fact/decision, then **Why:** and **How to apply:** lines; convert relative dates to absolute.
- `reference` — a pointer to where up-to-date information lives in an external system (tracker, dashboard, channel).

## Content Shape

- Lead with the rule/fact itself.
- Link related memories with `[[other-memory-name]]` (the slug from that file's `name:`, not a path) — a link to a name that doesn't exist yet is fine, it marks something worth writing later.
- Keep it concise: a memory file is a durable fact plus its rationale, not a transcript or a design doc.

## What never goes here (reject at the write gate)

- Code patterns, conventions, architecture, file paths — derivable by reading the current repo.
- Git history, recent changes, who-changed-what — `git log`/`git blame` are authoritative.
- Debugging solutions or fix recipes — the fix is in the code, the commit message has the context.
- Anything already documented in `AGENTS.md`/`CLAUDE.md`.
- Ephemeral task details: in-progress work, temporary state, current conversation context (that's `handoff.md`, via `session-handoff`).
- Secrets, credentials, tokens, private endpoints, customer data.

## Update vs. New File

Before writing, check `MEMORY.md` for an existing entry on the same topic. If one exists, update that file in place (edit its body, keep its `name`/type) and refresh the `MEMORY.md` hook text if needed; do not create a second file for a near-duplicate. Only create a new file when the topic is genuinely distinct.

## Tool Routing

- Recall: the index (`MEMORY.md`, already in context) first; `Read` a specific file only when more depth is needed.
- Write: `Write` (new file) or `Edit` (existing file), plus an `Edit` to `MEMORY.md`'s index line. No separate store/approval call exists in this environment — the file write *is* the persist step, so report it as `stored` only after the `Write`/`Edit` call actually succeeds, not merely after deciding to write.
- Cleanup/dedup across many memories: prefer the `anthropic-skills:consolidate-memory` skill when available instead of doing it ad hoc here.
