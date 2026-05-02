# Repeatable Evaluation Plan for Memory Inbox

## Purpose

`memory-inbox` needs a test loop that the agent can run repeatedly and judge without relying on subjective memory or live user input.

The first evaluation suite is scenario-based:

```text
tests/scenarios/<scenario>/input.md
              <scenario>/expected.yaml
```

A future implementation should transform each `input.md` into one candidate Markdown file with the expected metadata. In YOLO capture-first mode, even secret-like synthetic inputs become candidates; later consolidation decides whether to keep, transform, redact, archive, or reject them.

Then it compares behavior against `expected.yaml`.

## First Scenarios

| Scenario | Purpose |
|---|---|
| `001-explicit-user-sandbox-permission` | Safe explicit instruction should become a project-scoped candidate. |
| `002-secret-like-capture-first` | Secret-like synthetic content should become a candidate labeled for review, not be blocked. |
| `003-precompaction-session-summary` | Pre-compaction hook path should create an episode candidate. |

## Minimal Evaluation Command Shape

The future runner can be any language, but should behave like:

```bash
memory-inbox eval --scenarios memory/memory-inbox/tests/scenarios --tmp-output /tmp/memory-inbox-eval
```

Expected output:

```text
PASS 001-explicit-user-sandbox-permission
PASS 002-secret-like-capture-first
PASS 003-precompaction-session-summary
```

## Scoring Dimensions

Each scenario should be scored on:

1. **Decision correctness** — write exactly one candidate and apply the expected status, sensitivity, scope, retention, and triage flags.
2. **Schema correctness** — required metadata exists and enum values are valid.
3. **Content correctness** — required facts are included; forbidden claims are absent.
4. **Boundary correctness** — no active memory, consolidation, or index writes.
5. **Capture-first correctness** — hidden, sensitive, or secret-like synthetic content is not promoted to durable memory and is labeled for later review.
6. **Provenance correctness** — source and source agent are preserved.

## Manual Evaluation Checklist

Until an automated runner exists, the agent can evaluate a proposed implementation by reading the generated candidate and answering:

- Did it write exactly the number of files expected?
- Is the candidate status allowed for this scenario?
- Are `memory_type`, `scope`, `sensitivity`, `source`, and `retention` correct?
- Does the body contain all `must_include` ideas?
- Does the body avoid all `must_not_include` and `forbidden_literals`?
- Did it avoid writing outside the candidate output directory?
- Did it avoid calling or importing `memory-consolidator`?
- For capture-first scenarios, did it write a candidate instead of rejecting the input?
- For secret-like synthetic input, did it label the candidate with `sensitivity: secret-prohibited` and review triage flags?

## Capture-First Runner Expectations

- Every v0 scenario produces exactly one candidate file.
- Scenario 002 must have `status: needs_review`.
- Scenario 002 must have `sensitivity: secret-prohibited`.
- Scenario 002 must include `yolo_capture_first`, `secret_like_literal`, and `requires_human_review` triage flags.
- No scenario writes active memory, calls `memory-consolidator`, writes indexes, or writes outside the candidate directory.

## Product Rule

A Pi extension adapter is not acceptable until the CLI/library core can pass these scenarios. The extension must produce equivalent results for the same inputs.
