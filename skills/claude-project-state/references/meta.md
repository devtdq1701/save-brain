# Maintenance & Triggering (claude-project-state)

Maintainer-only notes. Not loaded at skill-trigger time; read when editing this skill or checking its triggering behavior.

## Verification

- Positive prompt: `update handoff for this completed phase`.
- Bootstrap prompt: `start this new project; create AGENTS.md if it is missing`.
- Pattern prompt: `we finished an important task; persist the durable project pattern`.
- Natural prompt: `should this rule go in AGENTS.md or the active plan?`
- Negative prompt: `fix this function in src/app.py`.
- Overlap prompt: `/save-brain after a useful procedure` should use this skill for handoff plus project-root `AGENTS.md` evaluation, and `claude-procedure-extraction` for reusable workflow candidates.

## Maintenance Notes

- Keep `description` under 1024 characters.
- Keep state-surface ownership in `references/policy-guide.md` and Markdown templates in `references/state-templates.md`.
- Keep this skill separate from `claude-state-memory`; state routing and Memory mutation gates have different risks.
