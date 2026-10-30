# Procedure Extraction Reference

## Primary Policy Ownership

This skill owns reusable procedure detection, candidate drafting, deduplication, approval gating, and persistence routing.

## Extraction Triggers

Consider extraction only when one of these is true:

- a non-trivial workflow was completed and verified;
- the workflow is likely to recur;
- a debugging path or workaround saved meaningful time;
- the user repeated the same correction;
- an active plan explicitly asks for procedure extraction.

Skip extraction for:

- one-time issues;
- trivial fixes;
- routine checkpoints;
- plan phase status;
- raw summaries;
- unverified ideas;
- content already captured elsewhere.

## Evidence Gate

Before drafting a candidate, collect bounded evidence:

1. Completed task.
2. Exact steps that worked.
3. Corrections or gotchas that changed the approach.
4. Inputs and outputs.
5. Verification that proved it worked.
6. Owner artifact: plan, doc, code, test, or handoff reference.

Reject the candidate if evidence is missing, unverifiable, sensitive, or too broad.

## Deduplication Gate

Check:

- repo-scoped skills;
- user-scoped skills when proposing cross-project reuse;
- project docs and active plans;
- project AGENTS guidance;
- Memory pointers when a local owner artifact already exists.

If an existing skill covers the workflow, propose a reference-file or skill update instead of a new skill.

## Classification

Classify as one:

- `new-skill`: new reusable workflow candidate.
- `skill-update`: existing skill needs improved instructions.
- `reference-file`: add detail under an existing skill's `references/`.
- `agents-guidance`: always-on project rule; route to AGENTS review.
- `memory-pointer`: short durable pointer after local owner exists and Memory gate passes.
- `skip`: not reusable, not verified, or already covered.

Default persistence is a candidate artifact in the active plan package. Do not create or update runtime skills, reference files, project AGENTS, or Memory pointers directly from detection.

## Candidate Template

Use `candidate-template.md` only after extraction, evidence, dedupe, and approval gates are relevant.

## Approval Gate

Ask the user before writing:

- candidate artifact;
- new skill;
- skill update;
- project AGENTS update;
- Memory pointer;
- cross-project user-scope artifact.

Memory pointer is allowed only after local owner artifact exists and the Memory write gate passes.
