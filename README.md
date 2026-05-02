# Memory System

Local-first agentic memory system for Pi. Captures candidate memory records, stores them in a durable backend, and supports retrieval.

## Architecture

```
capture → memory-inbox → candidates/ → memory-consolidator → storage → retrieval
```

**Current posture**: YOLO capture-first candidates now; consolidation/review later.

## Components

- [`memory/memory-inbox/`](memory/memory-inbox/) — **DONE**. Capture layer. Writes candidate Markdown records.
- [`memory/memory-consolidator/`](memory/memory-consolidator/) — **PLANNED**. Storage + retrieval layer. Gen1 plan at [`PLAN-GEN1.md`](memory/memory-consolidator/PLAN-GEN1.md).

## Active Documentation

- [`memory/README.md`](memory/README.md) — memory workspace hub
- [`memory/docs/design.md`](memory/docs/design.md) — high-level architecture
- [`memory/docs/inbox-consolidator-contract.md`](memory/docs/inbox-consolidator-contract.md) — candidate handoff contract
- [`memory/memory-inbox/README.md`](memory/memory-inbox/README.md) — memory-inbox entry point
- [`memory/memory-consolidator/PLAN-GEN1.md`](memory/memory-consolidator/PLAN-GEN1.md) — Gen1 consolidator plan

## Research & Tasks

- [`research/`](research/) — local agentic memory landscape analysis, critical review
- [`tasks/`](tasks/) — active task specifications

## Progress

| Component | Status | Tests |
|---|---|---|
| memory-inbox | ✅ Implemented | 13 passing |
| memory-consolidator | 📋 Planned (Gen1) | — |
| Pi extension adapter | ✅ Implemented | — |

See [`PROGRESS.md`](PROGRESS.md) for detailed milestone tracking.
