# Memory Inbox Progress

## Current Status

`memory-inbox` now has:

- deterministic Python CLI/library core;
- repeatable scenario evaluator;
- project-local Pi extension adapter;
- redacted adapter trace helper;
- candidate listing helper and `/memory-candidates` command bridge;
- unit tests for schema, capture, listing, scenarios, and adapter behavior.

Current MVP posture remains:

```text
YOLO capture-first candidates now; consolidation/review later.
```

## Implemented Files

Core:

- `pyproject.toml`
- `src/memory_inbox/schema.py`
- `src/memory_inbox/markdown.py`
- `src/memory_inbox/capture.py`
- `src/memory_inbox/candidates.py`
- `src/memory_inbox/scenarios.py`
- `src/memory_inbox/cli.py`
- `src/memory_inbox/tracing.py`
- `src/memory_inbox/pi_adapter.py`

Project-local Pi adapter:

- `../../.pi/extensions/memory-inbox/index.ts`
- `../../.pi/extensions/memory-inbox/adapter.py`
- `../../.pi/extensions/memory-inbox/README.md`

Tests:

- `tests/test_schema.py`
- `tests/test_capture.py`
- `tests/test_candidates.py`
- `tests/test_scenarios.py`
- `tests/test_pi_adapter.py`

## Validation Run

From `memory/memory-inbox`:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Result:

```text
Ran 13 tests
OK
```

Scenario evaluator:

```bash
PYTHONPATH=src python3 -m memory_inbox.cli eval \
  --scenarios tests/scenarios \
  --tmp-output .tmp/eval \
  --created-at 2026-04-27T00:00:00Z
```

Result:

```text
PASS 001-explicit-user-sandbox-permission
PASS 002-secret-like-capture-first
PASS 003-precompaction-session-summary
```

Project-local adapter smoke/list tests also passed:

- imported `.pi/extensions/memory-inbox/adapter.py`;
- called `memory_inbox_capture` and `memory_inbox_list`;
- wrote one candidate under `.tmp/pi-adapter-smoke/candidates`;
- validated the generated candidate;
- confirmed the adapter trace contains metadata but not raw captured secret-like text;
- confirmed no SQLite/DB/index files were created.

## Boundaries Preserved

- Candidate-only writes.
- No active durable memory promotion.
- No `memory-consolidator` calls.
- No index/embedding/database writes.
- Secret-like synthetic input is captured as a candidate, not blocked.
- Adapter traces redact raw captured text.

## Dogfood Candidate

Created a real `memory-inbox` candidate recording implementation progress:

```text
memory/candidates/20260427-120000-pre-compaction-memory-inbox-episode-fd6c82c8b2.md
```

## Next Product Step

Use `/reload` in Pi or start a new Pi session to load the project-local extension, then manually test the live tool:

```text
memory_inbox_capture
```

and command:

```text
/memory-inbox remember this test candidate
```

If live extension loading works, next implement listing/review commands for candidate files.

## Downstream: memory-consolidator

`memory-consolidator` is planned (Gen1). See [`../memory-consolidator/PLAN-GEN1.md`](../memory-consolidator/PLAN-GEN1.md) for scope, schema, and implementation order.
