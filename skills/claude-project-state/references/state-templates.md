# State Templates

Use this only when creating or reshaping project `AGENTS.md` or `handoff.md`.

When creating `AGENTS.md` automatically, keep only sections with project-specific content. Use `- None` only when an existing project template requires the section; otherwise omit empty optional sections.

## Root AGENTS Template

```markdown
# AGENTS.md - Project Instructions

## Project Scope

- These instructions apply to <repo/workspace scope>.
- Purpose: <one sentence>.
- Primary editable surfaces: <paths>.
- Do not copy global `~/.claude/CLAUDE.md`; add only project-specific overrides here.

## Source Of Truth

- <artifact/path>: <role>.
- Active plans live under `plans/<date>-<feature>/`.
- `handoff.md` is restart state only, not durable project policy.

## Repository Structure

- `<path>`: <role>.

## Architecture Constraints

- <durable architecture rule>.

## Commands And Verification

- After changing <surface>, run: `<command>`.

## Project-Specific Safety

- <repo-specific never rule>.

## Maintenance Rules

- Promote important durable project patterns to `AGENTS.md` when the project-state auto-update gate passes.
- Route reusable multi-step procedures to a skill/reference candidate instead of embedding the full procedure here.
- Keep this file concise; move procedures to skills and detailed decisions to plans/specs.
```

Omit sections that have no project-specific rules.

## Handoff Template

This is what `~/.claude/scripts/claude_save_brain.py` renders; it is shown for reading, not for copying. Produce a handoff by passing a JSON payload to that script, not by writing this Markdown by hand.

Section order:

```markdown
# Handoff

## Current Work

- Objective:
- Active package:
- Status:

## Working Set

- `<path>`

## Decisions

- <decision summary>; owner artifact: `<path>`.

## Verification

- <fresh check/result>.
- Skipped: <check and reason>, or `none`.

## Next Actions

- <next concrete action>, or `None`.

## Blockers

- <blocker and required input>, or `None`.
```

Optional sections may appear only after `Blockers` and in this order: `Notes`, `Risks`, `References`.
