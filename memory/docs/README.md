# Active Memory Documentation

This directory indexes the active documentation for the sandbox memory project.

## Canonical Active Docs

- [`design.md`](design.md) — high-level architecture and boundaries.
- [`inbox-consolidator-contract.md`](inbox-consolidator-contract.md) — active handoff contract for candidate Markdown records.
- [`../README.md`](../README.md) — memory workspace hub.
- [`../memory-inbox/README.md`](../memory-inbox/README.md) — active `memory-inbox` entry point.
- [`../memory-inbox/docs/product-decision.md`](../memory-inbox/docs/product-decision.md) — accepted product decision: Pi extension surface + deterministic CLI/library core.
- [`../memory-inbox/docs/repeatable-evaluation.md`](../memory-inbox/docs/repeatable-evaluation.md) — repeatable self-evaluation plan.
- [`../memory-inbox/tests/scenarios/README.md`](../memory-inbox/tests/scenarios/README.md) — scenario fixture index.

## Current Direction

`memory-inbox` is the active focus. Its MVP posture is:

```text
YOLO capture-first candidates now; consolidation/review later.
```

The inbox writes candidate records only. It does not promote candidates into active durable memory, rebuild indexes, create embeddings, or call `memory-consolidator`.

## Archive Markers

Archive markers live under [`archive/`](archive/). They record that older broad research/planning notes were removed from the active documentation surface. They are **not active requirements**.
