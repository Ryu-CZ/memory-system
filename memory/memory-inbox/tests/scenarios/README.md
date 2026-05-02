# Memory Inbox Repeatable Scenarios

These scenarios are the first self-evaluation suite for `memory-inbox`.

They are intentionally file-based and implementation-neutral. A future CLI, extension, or test runner should read each `input.md`, run the memory-inbox capture logic, and compare the produced candidate record against `expected.yaml`.

## Product Decision Under Test

`memory-inbox` is a Pi extension surface backed by a deterministic CLI/library core. These scenarios test the deterministic core. The Pi extension must eventually produce identical candidate records for the same inputs.

## How to Evaluate Manually

For each scenario:

1. Read `input.md`.
2. Confirm `memory-inbox` writes a candidate and applies the expected status, sensitivity, scope, retention, and triage metadata.
3. Compare the decision to `expected.yaml`.
4. Check that the proposed candidate contains required metadata and does not exceed the memory-inbox boundary.

## How to Evaluate Automatically Later

A future test runner should:

```text
for scenario in tests/scenarios/*:
  load input.md
  load expected.yaml
  run memory-inbox capture/precompact in temp dir
  validate exactly one output candidate and its metadata
  compare required fields and capture-first decisions
```

## Evaluation Rules

- Candidate Markdown must be written only to a configured candidate output directory.
- No scenario may write to active durable memory.
- No scenario may call `memory-consolidator`.
- Secret-like synthetic content must become a candidate in YOLO capture-first mode, labeled with `secret-prohibited` sensitivity and review triage flags.
- Candidate records must preserve provenance and scope.
- Candidate records should prefer narrow scope over global scope.

## Scenario Index

1. `001-explicit-user-sandbox-permission` — explicit user instruction should become a project-scoped candidate.
2. `002-secret-like-capture-first` — obvious synthetic credential-like content must be captured as a labeled candidate, not blocked.
3. `003-precompaction-session-summary` — a lossy-compaction moment should create an episode candidate with pre-compaction flags.
