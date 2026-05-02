# Memory Inbox Tests

Tests cover the deterministic CLI/library core for `memory-inbox`.

## Run

From `memory/memory-inbox`:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Run the repeatable scenario evaluator directly:

```bash
PYTHONPATH=src python3 -m memory_inbox.cli eval \
  --scenarios tests/scenarios \
  --tmp-output .tmp/eval \
  --created-at 2026-04-27T00:00:00Z
```

Expected scenario output:

```text
PASS 001-explicit-user-sandbox-permission
PASS 002-secret-like-capture-first
PASS 003-precompaction-session-summary
```

## Test Targets

- Candidate metadata validation.
- Permissive capture-first behavior for sensitive, hidden, and secret-like candidate inputs.
- Sensitivity classification and triage flag validation.
- Deterministic candidate IDs/files when `created_at` is fixed.
- Scope and retention preservation.
- Handoff file format compatibility with `memory-consolidator`.

## Boundary Checks

Tests should preserve the MVP boundary:

- write candidate Markdown only;
- no active durable memory;
- no `memory-consolidator` calls;
- no indexes, embeddings, SQLite, or cache writes;
- no writes outside the configured candidate output directory.
