# Memory Inbox

`memory-inbox` is the capture and triage layer for the memory workspace.

## Product Decision

`memory-inbox` will be a **Pi extension product surface backed by a deterministic CLI/library core**.

- The Pi extension is the always-available agent-facing integration.
- The CLI/library core owns validation, deterministic normalization, provenance preservation, and candidate writing.
- The extension must call the same core behavior that tests evaluate.
- `memory-inbox` is not a subagent.
- `memory-inbox` never promotes candidates into active durable memory.

See [`docs/product-decision.md`](docs/product-decision.md) for the full decision.

## Start Here

- [`docs/product-decision.md`](docs/product-decision.md) — accepted product decision and YOLO capture-first policy.
- [`docs/repeatable-evaluation.md`](docs/repeatable-evaluation.md) — scenario-based self-evaluation plan.
- [`../docs/inbox-consolidator-contract.md`](../docs/inbox-consolidator-contract.md) — candidate handoff contract.
- [`tests/scenarios/README.md`](tests/scenarios/README.md) — repeatable scenario fixtures.
- [`PROGRESS.md`](PROGRESS.md) — current implementation progress and validation trace.

## Purpose

Accept raw or semi-structured memory candidates and turn them into scoped candidate Markdown records that are ready for later review by `memory-consolidator`.

Early `memory-inbox` development is permissive and capture-first: prefer writing a candidate with metadata over rejecting input. Think of it like a TTRPG AI dungeon master notebook: hidden lore and messy session facts may be captured because the later consolidator decides what becomes canon.

## Inputs

- User-explicit facts.
- Project observations.
- Summaries from agent work.
- Candidate notes imported from local sandbox workflows.

## Outputs

- Scoped candidate Markdown records.
- Metadata sufficient for review, consolidation, retention decisions, later rejection, or later promotion by `memory-consolidator`.
- Handoff files compatible with the inbox/consolidator contract in `../docs/inbox-consolidator-contract.md`.

## Non-goals

- No durable promotion of memory to canonical status.
- No deduplication authority over the canonical corpus.
- No ownership of generated caches, indexes, embeddings, or database files.
- No durable promotion of sensitive, secret-like, or messy captured material into canonical memory.
- No security-first rejection gate in the MVP; capture-first candidates may carry sensitivity and triage metadata for later consolidation.

## Implementation Status

The deterministic Python CLI/library core exists and passes the repeatable scenarios. A project-local Pi extension adapter also exists under `.pi/extensions/memory-inbox/`.

The TypeScript extension registers a tool/command/hook and calls the Python adapter/core. Live use still requires Pi to reload project extensions.

## Run

From this directory:

```bash
PYTHONPATH=src python3 -m memory_inbox.cli --help
```

Run the scenario evaluator:

```bash
PYTHONPATH=src python3 -m memory_inbox.cli eval \
  --scenarios tests/scenarios \
  --tmp-output .tmp/eval \
  --created-at 2026-04-27T00:00:00Z
```

Run unit tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Commands

- `memory-inbox capture` — capture one candidate Markdown record.
- `memory-inbox precompact` — capture a pre-compaction episode candidate.
- `memory-inbox validate` — validate a candidate Markdown file.
- `memory-inbox list` — list candidate Markdown records.
- `memory-inbox eval` — run repeatable scenario fixtures.

## Project-local Pi Adapter

Files:

- `../../.pi/extensions/memory-inbox/index.ts` — project-local Pi extension.
- `../../.pi/extensions/memory-inbox/adapter.py` — import bridge for tests and future Python tooling.
- `src/memory_inbox/pi_adapter.py` — adapter functions over the deterministic core.
- `src/memory_inbox/tracing.py` — redacted JSONL trace helper.

Registered Pi surface in `index.ts`:

- tool: `memory_inbox_capture`
- command: `/memory-inbox`
- command: `/memory-candidates`
- hook: `session_before_compact`

Adapter traces are generated under `.tmp/pi-adapter/` or a caller-provided trace path. Traces are generated artifacts and should not contain raw captured text or secret-like literals.

When not installed as a console script, use:

```bash
PYTHONPATH=src python3 -m memory_inbox.cli <command>
```
