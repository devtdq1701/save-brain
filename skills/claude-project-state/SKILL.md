---
name: claude-project-state
description: "Use this skill when deciding which local surface owns a fact - root AGENTS.md, root handoff.md, an active plan package, or auto-memory - and when creating, updating, or validating project-root AGENTS.md, or promoting a project pattern into durable guidance. Triggers: where should this rule live, promote this to AGENTS.md, project has no AGENTS.md, durable project guidance, state surface boundary, luat nay de dau, tao AGENTS.md cho project, save-brain, save brain, save-state, save state, checkpoint everything, luu trang thai. Do not use for ordinary code edits, external version facts, reusable procedure extraction, global preferences, or auto-memory schema/cleanup. Use session-handoff only for handoff-only requests; full save-brain/full state-save requests start here. Output: target state surface, rationale, minimal update scope, and verification."
---

# Claude Project State

## Purpose

Own exactly one reusable workflow:

- Job: route facts to the correct local state surface without duplication.
- Primary surfaces: root-owned `AGENTS.md`, root-owned `handoff.md`, active plan packages, and compact plan indexes.
- Non-goals: auto-memory gates and schema, reusable procedure extraction, raw session summaries, or global user preferences.

## Use When

- The user asks to update handoff, AGENTS, brain, project state, or durable repo instructions.
- A new project or workspace lacks root `AGENTS.md` and local evidence can define durable project guidance.
- Current work state changed after a phase, slice, or meaningful decision.
- An important completed task revealed a project-specific pattern, source-of-truth rule, verification command, safety rule, or repeated correction that should affect future sessions.
- A plan phase needs state refresh without duplicating plan details.

## Skip When

- The task is a direct code or doc edit with a clear target and no state-boundary question.
- The information is an external product or version fact.
- The content is a reusable multi-step procedure; use `claude-procedure-extraction`.
- The content is a global preference or global user instruction; it belongs in global `~/.claude/CLAUDE.md`, not project state.
- The task is specifically auto-memory schema, cleanup, or write gates; use `claude-state-memory`.

## Inputs

- Required: fact or state update, intended lifetime, and likely owner artifact.
- Optional: active plan package, current handoff, AGENTS scope, prior decision note.
- Reference files: `references/policy-guide.md`, `references/state-templates.md`.

## Workflow

1. Classify the fact by lifetime: durable repo rule, restart state, detailed plan evidence, durable recall hint, or no stored state.
2. Choose one owner surface and its canonical state root: root-owned `AGENTS.md`, root-owned `handoff.md`, active plan, auto-memory handoff to `claude-state-memory`, or no update.
3. Resolve the canonical state root once, then use the same root for both `AGENTS.md` and `handoff.md` unless the user explicitly requests separate roots.
4. Keep `handoff.md` compact and restart-oriented; link to plan artifacts for detail, and resolve the correct canonical state root before writing it.
5. Keep `AGENTS.md` at the canonical state root, project-specific, and stable; never use it as a session log.
6. Apply the `AGENTS.md` entry admission filter in `references/policy-guide.md`; omit candidates that are self-discoverable, lack a specific consequence, cannot be verified, or conflict with another instruction scope.
7. Write every `AGENTS.md` in English and conform it to the Root AGENTS Template in `references/state-templates.md`; copying, migrating, or rewriting content never preserves the source language/layout or waives template compliance.
8. For missing root `AGENTS.md`, gather local evidence first. For non-trivial projects, use bounded read-only subagents when delegation is authorized, then main creates the file from fan-in evidence.
9. **Full state-save sweep** - this skill owns the definition; other skills reference it instead of restating it. Triggered by "save-brain", "save brain", "save-state", "save state", "checkpoint everything", "luu trang thai". Run in order and report every step, including the ones that decide to skip: (a) resolve the canonical root; (b) read the current `handoff.md` first and carry over every unfinished Next Action/Blocker (or mark it done), then write and validate it through `claude_save_brain.py`; the script copies an uncommitted or untracked `handoff.md`/`AGENTS.md` to `<root>/.archived/` before overwriting and lists it in `archived_files` - report that path; (c) run the `AGENTS.md` create/update checklist at the same root and apply it when it passes; (d) hand reusable-procedure candidates to `claude-procedure-extraction`; (e) hand the durable-recall decision to `claude-state-memory`; (f) state commit status explicitly - commit the local-state artifacts when they live in a kept git repo/worktree, otherwise report them as local-only. The run is incomplete until the report contains an explicit result for all four gates: project-state, session-handoff, procedure-extraction, and state-memory.
   Required receipt: `project-state=...`, `session-handoff=...`, `procedure-extraction=...`, `state-memory=...`, `memory=stored|skipped`, and `commit=...`.
10. For important completed-work patterns, stage the candidate in the active plan or handoff first; promote it into `AGENTS.md` only after two repeats or an explicit user decision about that exact rule, and only when it is durable project guidance and passes the admission filter. Route reusable multi-step procedures to `claude-procedure-extraction` instead.
11. Verify the updated surface has the expected schema, resolved root, and no duplication with another owner.

## Progressive Disclosure

- Read `references/policy-guide.md` when routing state, applying ownership boundaries, deciding promotion rules, or creating/updating `AGENTS.md`.
- Read `references/state-templates.md` only when creating or reshaping root-owned `AGENTS.md` or `handoff.md`.
- Write `handoff.md` and project-root `AGENTS.md` through `python3 ~/.claude/scripts/claude_save_brain.py --project-root <root>` with a JSON payload on stdin. It renders the canonical sections, enforces the section/line/character budgets, and refuses the write on hard failure. Do not hand-write either file when the script can render it.

## Output Contract

Return:

- target state surface;
- rationale;
- minimal update scope;
- verification check or skipped-check reason.

Do not return:

- full artifact dumps;
- global instruction copies;
- raw session history.

<!-- Triggering prompts and maintenance notes moved to references/meta.md (not loaded at trigger time). -->
