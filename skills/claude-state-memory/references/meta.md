# Maintenance & Triggering (claude-state-memory)

Maintainer-only notes. Not loaded at skill-trigger time; read when editing this skill or checking its triggering behavior.

## Verification

- Positive prompt: `save-brain, should this be remembered?`
- Natural prompt: `what do you remember about our memory policy?`
- Negative prompt: `edit this Markdown typo`.
- Overlap prompt: `update handoff, refresh AGENTS, and maybe remember the durable decision` should combine this skill with `claude-project-state`.

## Maintenance Notes

- Keep `description` reasonably short and specific (no hard character limit documented for Claude Code skills as of this port; match the other three ported skills' length as a rule of thumb).
- Keep memory gates in `references/policy-guide.md` and entry schema in `references/memory-schema.md`.
- Do not let a sub-agent write memory files directly — route the candidate back to the main agent.
- Ported from Codex's `codex-state-memory` 2026-10-22; re-sync manually if the Codex source changes meaningfully.
