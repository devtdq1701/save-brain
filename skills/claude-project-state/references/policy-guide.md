# Project State Reference

## Primary Policy Ownership

This skill owns state-surface routing between durable project guidance, current restart state, detailed plan evidence, and optional Memory handoff.

## Surface Ownership

| Surface | Owns | Must Not Own |
| --- | --- | --- |
| Root `AGENTS.md` | Durable project/workspace guidance, source-of-truth routing, verification commands, repo-specific constraints | Current task status, temporary plan state, global communication rules, raw correction history |
| `handoff.md` | Short restart state, active objective, working set, latest decisions, verification, next actions, blockers | Durable repo policy, onboarding docs, full specs, copied plan content |
| Active plan package | Detailed decisions, acceptance criteria, phase status, implementation notes, verification evidence | Global preferences, raw command logs, unrelated conventions |
| Auto-memory (`~/.claude/projects/<slug>/memory/`) | Concise durable recall hints after a separate Memory gate | Current work source of truth, external version facts, active plan state |
| Skill | Reusable workflow for deciding and maintaining boundaries | Persistent project state itself or hidden writes |

## Handoff Schema

Keep handoff compact and restart-oriented. Use `state-templates.md` when creating or reshaping `handoff.md`.

Handoff path resolution: the canonical state root is the current workspace (the session's working directory) unless the user's prompt names another root. `handoff.md` and `AGENTS.md` both live there unless the prompt asks for separate roots. Do not move the root on your own to a repository root, an ancestor, or a nested repo or worktree, and do not create a second `handoff.md` there. Legacy `.brain/handoff.md` and `.brain/handover.md` are read for recall only when the root has no `handoff.md`; writes always go to the root `handoff.md`.

Write `handoff.md` only when the active command or user request permits state mutation. Read-only commands must report the needed update instead of mutating handoff. Handoff content is English by default so restart state remains compact and consistent. In a full state-save sweep, local state is not current until the canonical handoff path is resolved, the handoff is written and validated there, the root `AGENTS.md` create/update gate is evaluated at the same root and applied when it passes, and local-state commit status is made explicit: commit the affected local-state artifacts if they live inside a kept git repo/worktree; otherwise report them as local-only instead of implying a commit.

Validate canonical handoff headings and order after writes. If validation fails, treat it as a hard failure, report it, and do not claim state was saved. Keep handoff bounded; detailed evidence belongs in the active plan package.

Heading order, empty-section rendering, and every size budget are enforced in code by `~/.claude/scripts/claude_save_brain.py` (`HANDOFF_ITEM_BUDGETS`, `HANDOFF_TOTAL_BUDGETS`). Write through that script rather than editing `handoff.md` by hand, and do not restate the numbers here or in a skill body: one copy in code, no second copy to drift. The writer refuses the write on hard failure, so an over-budget handoff cannot be saved silently.

## Root AGENTS Guidance

Root `AGENTS.md` should contain only durable guidance for the resolved state root. Do not copy global instructions. Add only project/workspace-specific overrides. Use `state-templates.md` when reshaping the file.

Canonical path resolution: root `AGENTS.md` lives at the same canonical state root as `handoff.md` (see Handoff path resolution). If an ancestor `AGENTS.md` already scopes to this workspace, do not duplicate its rules here; report it instead.

### What is mechanically enforced

`~/.claude/scripts/claude_save_brain.py` is the only thing that actually blocks a bad write. It enforces exactly two AGENTS.md rules and nothing else:

| Check | Level | Behavior |
| --- | --- | --- |
| A handoff-only section (`Current Work`, `Working Set`, `Next Actions`, `Blockers`, `Progress`) appears in `AGENTS.md` | hard failure | refuses the write, exits 2 |
| A heading outside the Root AGENTS Template | drift warning | reports `status=drift`, still writes |

Everything below this line is a **self-review checklist, not a gate**. No script checks it; the agent applies it and must say which item rejected a candidate and why. Do not assume a rule is enforced because it is written down.

### Entry Admission Checklist (self-review, not enforced)

Before adding or retaining an `AGENTS.md` entry, answer all four questions:

1. **Can the agent discover it quickly?** Omit directory trees, module catalogs, manifest facts, and file descriptions that `rg`, `rg --files`, project manifests, or nearby docs reveal in seconds. Keep only a non-obvious source-of-truth, precedence, or behavioral constraint.
2. **What specific failure or cost does the entry prevent?** Keep it only when the answer names a concrete wrong action or avoidable cost, such as running `npm install` in a pnpm workspace. "Better context" is not sufficient.
3. **Can a future agent verify it?** Express the entry as a command, path, format, condition, or observable invariant. Rewrite vague advice such as "keep code clean" into a measurable project constraint or omit it.
4. **Does it conflict with another instruction scope?** Compare global, parent, current-root, and nested `AGENTS.md` rules. Resolve the conflict in the owning instruction or establish effective scope and precedence before writing. Merely noting the conflict or asserting an override while the contradictory rule remains is not resolution.

Apply a timing gate as well: add a rule only from stable repository evidence, an explicit user decision about that exact rule, or a repeated correction that meets the promotion threshold below. A blanket request to capture all useful context does not waive the admission filter or promotion threshold. Stage one-off corrections in the active plan or handoff instead of preemptively expanding `AGENTS.md`.

In a full state-save sweep, evaluate the canonical root `AGENTS.md` create/update checklist immediately after handoff resolution. If the gate passes, write or update `AGENTS.md` at the same resolved root, validate its schema, and handle its commit status explicitly when it lives inside a kept git repo/worktree.

### Auto-Create Checklist (self-review, not enforced)

Create root `AGENTS.md` automatically when all are true:

- the resolved state root has no `AGENTS.md`;
- no broader root `AGENTS.md` already scopes to the current project/workspace;
- local evidence identifies project scope, source-of-truth files, repository structure, constraints, or verification commands;
- the content is project-specific and durable, not session status or global preference;
- every candidate entry passes the entry admission filter;
- main session owns the final write and verifies the resulting format.

For non-trivial project bootstrap, use read-only subagents when delegation is authorized:

- one subagent maps repository structure and source-of-truth artifacts;
- one subagent maps commands, tests, tooling, and verification;
- one subagent maps risks, safety rules, secrets boundaries, and project-specific constraints.

Fan in their outputs, dedupe claims, and create only the distilled `AGENTS.md` guidance. Do not paste raw subagent summaries.

### Auto-Update Checklist (self-review, not enforced)

Update root `AGENTS.md` automatically after important work when all are true:

- the completed work produced a durable project rule, source-of-truth routing decision, verification command, architecture constraint, safety rule, or recurring project-specific pattern;
- the rule will improve future sessions across more than the current task;
- the rule is concise and belongs under an existing AGENTS section;
- the rule passes the entry admission filter;
- the rule meets the timing gate: stable repository evidence, an explicit user decision about that exact rule, or two repeats;
- the detail is not already owned by an active plan, spec, skill, reference file, or `handoff.md`.

A full state-save sweep must evaluate this auto-update checklist by default. Do not leave durable project guidance only in `handoff.md` when it belongs in root `AGENTS.md`.

Do not update `AGENTS.md` for:

- current phase status, next actions, temporary blockers, or verification logs;
- raw correction history;
- long reusable procedures that should become a skill/reference candidate;
- sensitive values, credentials, or private endpoints.
- global preferences or global user instructions; route those to global `~/.claude/CLAUDE.md` instead.

If a repeated correction should become durable:

1. Stage it in the active plan or handoff as a candidate.
2. Promote it to `AGENTS.md` after two repeats or an explicit user decision about that exact rule, and only when it passes the admission filter.
3. Promote the distilled rule, not raw correction history.

## Active Plan Package Rules

Use active plan packages for:

- detailed decisions;
- acceptance criteria;
- phase status;
- research;
- implementation notes;
- verification evidence.

Use root `plans.md` only as a compact index.

## Verification Checks

After updating state:

- check required handoff headings and order;
- check that `AGENTS.md` lives at the same canonical state root as `handoff.md` unless the user explicitly requested separate roots;
- check that AGENTS contains durable project guidance only;
- check that every added or retained entry passes the entry admission filter;
- check that parent/current/nested instruction conflicts are resolved explicitly;
- check that AGENTS follows `state-templates.md` section intent when newly created or reshaped;
- check that detailed phase evidence stays in the plan package;
- state any skipped state update and residual risk.
