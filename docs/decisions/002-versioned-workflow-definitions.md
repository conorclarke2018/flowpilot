# ADR-002: Versioned, immutable JSON workflow definitions

## Status

Accepted

## Context

A workflow is user-authored (via the visual editor) and needs to be: edited
freely while in progress, executed deterministically once published, and
referenced unambiguously by every run it ever produces — including runs that
start today against a definition from three edits ago.

## Decision

Separate "draft" from "published" at the schema level:

- `workflows.draft_definition` (JSONB) — the live, freely-editable graph.
  `PUT /workflows/{id}` overwrites it and bumps `draft_revision`.
- `workflow_versions` — an **append-only** table. `POST /workflows/{id}/publish`
  validates the current draft (`app/engine/validation.py`) and, only if valid,
  snapshots it into a new row with an incrementing `version` integer. Existing
  rows are never updated.
- `workflow_runs.workflow_version` stores the exact integer version a run
  started against, and `execute_run` loads that specific `WorkflowVersion` row
  — never the live draft — before executing (`app/services/runs.py`).

The graph itself (`app/schemas/workflow_definition.py`) is a small, explicit
Pydantic contract: `WorkflowDefinition { name, nodes: [...], edges: [...] }`,
shared verbatim between manual editing, AI generation (ADR-004), and execution.
There's exactly one definition of what a valid workflow graph looks like.

## Alternatives considered

- **Single `definition` column, no versioning**: rejected. This was tested
  implicitly during development — editing a workflow's draft while a run was
  mid-execution against it would have silently changed what "the workflow"
  meant for an in-flight run. Since runs can pause for days waiting on human
  approval (ADR-006), this isn't a theoretical edge case.
- **Git-style content-addressed definitions (hash the JSON)**: rejected as
  over-engineered for the actual requirement, which is "runs pin to what they
  started with" — a simple incrementing integer per workflow does that with an
  `ORDER BY version` query and a unique constraint, no hashing needed.

## Consequences

- Publishing is the only path to a version that's immutable, which, combined
  with validation-before-snapshot, is what makes the acceptance test
  "published versions remain unchanged when a draft is edited" actually true
  rather than aspirational — it's enforced by the table structure, not by
  convention.
- Cost: every published workflow accumulates versions forever (no pruning).
  Acceptable at current scale; would need a retention policy before this
  becomes a real product.
