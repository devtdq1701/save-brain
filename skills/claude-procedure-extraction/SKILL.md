---
name: claude-procedure-extraction
description: "Use this skill when a verified procedure, repeated correction, debug recipe, or operational recipe is likely to recur and may deserve a skill or reference file. Triggers: turn this into a skill, save this procedure, we keep repeating this, extract this workflow, bien quy trinh nay thanh skill. Do not use for routine checkpoints, one-off bugs, unverified ideas, raw summaries, procedures already covered by an existing skill, or external version facts. Output: accepted/rejected candidates, evidence, dedupe result, proposed owner target, approval needed, and persistence constraints."
---

# Claude Procedure Extraction

## Purpose

Own exactly one reusable workflow:

- Job: detect verified reusable procedures and shape them into approval-gated skill or reference candidates.
- Primary surfaces: full state-save sweeps, explicit extraction requests, completed sessions, repeated corrections, debug recipes, operational workflows.
- Non-goals: routine checkpointing, handoff compaction, auto-memory writes, automatic skill creation, or automatic reference-file creation.

## Use When

- A non-trivial workflow was executed successfully and is likely to recur.
- verified debug recipes, workarounds, tool sequences, or operational recipes saved meaningful time.
- The user repeatedly corrected the agent on the same procedure.
- An important completed task revealed a reusable procedure or recipe likely to become a skill or reference candidate.
- An active plan explicitly asks for procedure extraction.

## Skip When

- The session only contains routine checkpoint, plan status, verification log, typo, or one-off fix.
- The procedure is already captured in an existing skill, doc, active plan, or AGENTS rule.
- Evidence is missing, unverified, sensitive, or based only on external version facts.

## Inputs

- Required: completed task evidence, working steps, gotchas, inputs, outputs, verification, and likely owner artifact.
- Optional: existing skill list, docs/plans search results, candidate scope, target persistence surface.
- Reference files: `references/policy-guide.md`, `references/candidate-template.md`.

## Workflow

0. In a full state-save sweep this skill is only the reusable-procedure step. The sweep is defined by `claude-project-state` (step 9); do not restate its steps here.
1. Confirm local handoff or plan state is current before extracting procedure candidates.
2. Apply the evidence gate: task, steps, gotchas, inputs, outputs, verification, and owner artifact.
3. Deduplicate against existing skills, project docs, AGENTS guidance, active plans, and Memory pointers.
4. Classify the candidate as new skill, skill update, reference file, or skip. If it is really a durable project rule or a Memory-worthy fact (not a reusable procedure), hand it off to `claude-project-state` or `claude-state-memory` instead of classifying it here.
5. Do not write `AGENTS.md` or auto-memory from this skill; those surfaces are owned by `claude-project-state` and `claude-state-memory`.
6. Ask for approval and do not write a candidate artifact, skill file, or reference file without it.

## Progressive Disclosure

- Read `references/policy-guide.md` when applying extraction, evidence, dedupe, classification, or approval gates.
- Read `references/candidate-template.md` only when drafting an approval-gated candidate.
- No script enforces candidate quality. Every gate in this skill is a judgment check the agent applies itself, so state explicitly which gate rejected a candidate and why. For the dedupe gate, check the session's available-skills list (plugin skills included) and `~/.claude/skills` before claiming a candidate is new.

## Output Contract

Return:

- candidate classification;
- evidence summary;
- dedupe result;
- accepted candidates and rejected candidates;
- proposed owner surface or file target;
- approval needed for persistence;
- verification prompts for the candidate.

Do not return:

- raw transcript;
- sensitive details;
- automatic persistence claims;
- a final skill/reference file unless the user approved that write.

<!-- Triggering prompts and maintenance notes moved to references/meta.md (not loaded at trigger time). -->
