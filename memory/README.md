# Memory Workspace

This directory is the active sandbox workspace for the local memory architecture project inside `/home/trval/projects/chats/pi_sandbox`.

## Current Focus

The active development focus is [`memory-inbox/`](memory-inbox/).

Current product posture:

```text
YOLO capture-first candidates now; consolidation/review later.
```

`memory-inbox` captures candidate Markdown records. It does not decide final memory truth.

## Source of Truth

Candidate and durable memory records should be human-readable Markdown. Generated artifacts such as indexes, caches, embeddings, logs, or databases are rebuildable unless a future active design document explicitly says otherwise.

Derived files may support retrieval and automation, but they are not the source of truth.

## Active Docs

Start here:

- [`docs/README.md`](docs/README.md) — active documentation index.
- [`docs/design.md`](docs/design.md) — high-level architecture.
- [`docs/inbox-consolidator-contract.md`](docs/inbox-consolidator-contract.md) — candidate handoff contract.
- [`memory-inbox/README.md`](memory-inbox/README.md) — `memory-inbox` entry point.
- [`memory-inbox/docs/product-decision.md`](memory-inbox/docs/product-decision.md) — accepted runtime/product decision.
- [`memory-inbox/docs/repeatable-evaluation.md`](memory-inbox/docs/repeatable-evaluation.md) — repeatable scenario evaluation.

## Subprojects

- [`memory-inbox/`](memory-inbox/) — active MVP. Captures raw or semi-structured inputs into candidate Markdown records under [`candidates/`](candidates/).
- [`memory-consolidator/`](memory-consolidator/) — downstream/deferred. Later reviews candidates, decides promotion/rejection/merge behavior, and may rebuild derived indexes.

## Candidate Handoff

Candidate records are written to:

```text
memory/candidates/
```

Only `memory-inbox` should write new candidate records there during the MVP. `memory-consolidator` consumes them later.

## Archive Markers

Historical research and pre-pivot plans were removed from the active documentation surface. [`docs/archive/`](docs/archive/) contains marker notes explaining that cleanup. Archive markers do not override active docs.
