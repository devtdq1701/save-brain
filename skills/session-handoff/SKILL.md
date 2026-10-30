---
name: session-handoff
description: Save current session progress as local handoff state only. Use when the user asks to save session state, checkpoint progress, prepare a handoff, update handoff.md, or preserve resume context without writing durable memory, for handoff-only requests. Do not use as the sole handler for save-brain/full state-save requests; start those with claude-project-state. The only persistence target is handoff.md; AGENTS.md changes go through claude-project-state.
---

# Session Handoff

## Overview

Keep transient session progress out of durable memory. Write enough local state for the next agent/session to resume. `AGENTS.md` belongs to `claude-project-state`; this skill never edits it.

## Persistence Rules

- Do not write to the durable auto-memory files (`~/.claude/projects/<project>/memory/`) for session progress — that is `claude-state-memory`'s surface, not this skill's.
- Do not store transcripts, raw logs, secrets, credentials, tokens, private endpoints, or customer data.
- Do not edit unrelated files.
- Preserve restart-relevant content; `Next Actions` is a carry-forward ledger (rule in `Writing the handoff`).
- Compact background and finished history when needed, but never drop an open `Next Actions` item to satisfy a size budget. Combine wording only when every unfinished obligation remains represented; if that still cannot fit, stop and report the validation failure.
- Prefer local evidence from git, tests, docs, and command output over conversation recall.

## Target Files

- Handoff: exactly one `handoff.md` at the canonical state root defined in `claude-project-state` `references/policy-guide.md` (Handoff path resolution): the current workspace unless the user's prompt names another root.

## Workflow

1. Identify the active workspace/folder root, active repository, branch, worktree, and feature name when available.
2. Check current state with bounded commands such as `git status --short --branch`, recent commits, active docs, and recent verification results. When there is no repo, no source tree, or the evidence is not on this machine, skip this step and mark the affected facts as unverified recall in the payload instead of inventing evidence.
3. Resolve the handoff path per `Target Files` and state it in the report.
4. Build the resume packet as a JSON payload and write it with the shared writer (see `Writing the handoff` below). Carry `Next Actions` forward per `Writing the handoff`. Do not hand-write the Markdown. If the existing handoff already covers the session with nothing to add, drop, or correct, skip the write and report it as already current - a no-op rewrite is churn, not a checkpoint.
5. If the session surfaced durable project guidance, name it in the report and route it to `claude-project-state`; do not edit `AGENTS.md` here.
6. Verify by reading back the changed handoff section. Report paths changed, the writer's validation status, and any skipped checks.

## Writing the handoff

`~/.claude/scripts/claude_save_brain.py` owns the file format. It renders the canonical sections in the required order, fills empty sections with `None`, enforces the size budgets, and refuses the write when a hard budget is exceeded. Never hand-write `handoff.md`: a hand-written file bypasses the only check that keeps it short.

**The writer REPLACES the whole file. It does not merge or append.** Whatever is not in your payload is gone. So when `handoff.md` already exists: read it first, compare `Next Actions` item by item, and carry forward every item that lacks explicit completion evidence. A task is not removable because it is old, absent from the current session, or presumed stale. Dropping or materially changing a task requires recording what completed it and the evidence path/result in the same payload; otherwise preserve the original obligation. This read-decide-carry step is mandatory, never a side effect of forgetting to include it.

```bash
python3 ~/.claude/scripts/claude_save_brain.py --project-root <resolved-root> <<'JSON'
{
  "handoff": {
    "current_work": ["Objective: ...", "Status: ..."],
    "working_set": ["path/to/file.py:42"],
    "decisions": ["Chose X over Y because ..."],
    "verification": ["`pytest tests/` -> 20 passed"],
    "next_actions": [],
    "blockers": []
  }
}
JSON
```

Payload rules:

- Use exactly the keys `current_work`, `working_set`, `decisions`, `verification`, `next_actions`, `blockers`, plus optional `notes`, `risks`, `references`. The writer also maps a few legacy keys and rejects anything else; there is no `progress` section.
- Choosing between the overlapping sections: `blockers` = work is stopped until someone else acts (missing credentials, unanswered question). `risks` = work continues but something may bite later (a known gap, an unverified assumption). `next_actions` = you can do it yourself right now. A problem found but deliberately left unfixed is a `risks` item, and belongs in `next_actions` too only if you intend to fix it. `notes` = context that helps a restart but implies no action. `references` = pointers to plans, specs, tickets, or evidence directories.
- When the session's facts cannot be re-derived from the local repo (work done on a remote host, workspace moved, evidence not on disk), still record them, and say so in the same bullet - for example "unverified recall: ...". Never silently present recall as verified evidence.
- Write each bullet dense and short: the fact plus its path or evidence, no narration. When content exceeds a budget, cut in this order: finished work first, then background/history, then detail behind a `file:line` or plan-path pointer. Never cut an open blocker, an unverified assumption, or the next concrete action. If a cut still drops context a restart would need, tell the user in the report what was dropped and where the full detail lives.
- Values are a string or a list of strings; one list item becomes one bullet.
- Leave `next_actions`/`blockers` as `[]` when nothing is pending; the writer renders `None`.
- Exit 2 with `handoff validation failed: ...` means nothing was written; the message names each over-budget section with its count and limit. Cut content and retry; do not work around it by writing the file directly.

## Output Contract

Return:

- handoff path updated;
- durable-guidance candidates routed to `claude-project-state`, or `none`;
- verification performed;
- next resume instruction.

Do not return raw secrets, long logs, or full transcripts.
