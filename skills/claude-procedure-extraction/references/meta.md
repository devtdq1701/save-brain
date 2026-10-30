# Maintenance & Triggering (claude-procedure-extraction)

Maintainer-only notes. Not loaded at skill-trigger time; read when editing this skill or checking its triggering behavior.

## Verification

- Positive prompt: `/save-brain extract any reusable procedure from this completed workflow`.
- Natural prompt: `turn the repeated SSL renewal workflow into a skill candidate`.
- Negative prompt: `record this phase checkpoint`.
- Overlap prompt: `save state and remember the durable procedure` should combine this skill with `claude-project-state` and `claude-state-memory`.

## Maintenance Notes

- Keep `description` under 1024 characters.
- Keep procedure gates in `references/policy-guide.md` and candidate shape in `references/candidate-template.md`.
- Do not migrate legacy learned skills unless the user explicitly asks for that separate track.
