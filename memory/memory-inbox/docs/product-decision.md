# Product Decision: Memory Inbox Runtime Shape

## Decision

Status: accepted for MVP planning.

`memory-inbox` will be a **Pi extension product surface backed by a deterministic CLI/library core**.

This means:

- The **Pi extension** is the always-available agent-facing integration.
- The **CLI/library core** owns schema validation, deterministic normalization, provenance preservation, candidate writing, and repeatable behavior.
- The extension must call the same core behavior as tests and CLI commands.
- `memory-inbox` is **not** a subagent.
- `memory-inbox` is **not** the memory consolidator.
- `memory-inbox` creates candidate records only; it never promotes candidates into active durable memory.

Short product phrase:

> Always available in Pi, deterministic at the core, candidate-only by design.

## Capture Policy: Permissive YOLO Capture-First

Early `memory-inbox` development is **capture-first**, not security-first.

Use the TTRPG AI dungeon master metaphor: the inbox is allowed to capture hidden lore, private campaign facts, unresolved twists, and messy session details because the DM needs to know them. In this phase, safety/security screening should not dominate the product or slow down exploration.

The inbox should prefer:

```text
capture candidate now -> let consolidator/reviewer decide later
```

rather than:

```text
reject early -> lose potentially useful memory
```

For v0, classification is metadata, not a hard blocker. Secret-like or sensitive-looking input may be captured as a candidate with explicit `sensitivity` and `triage_flags`. The important boundary is that `memory-inbox` writes **candidates only**. It does not promote candidates into active durable memory, indexes, profile facts, or procedures.

Security, redaction, approval, deletion, and promotion policy can be added later in `memory-consolidator` or future memory services.

## Why Extension + CLI Core

### Why a Pi extension

A Pi extension is the correct product surface because `memory-inbox` needs to be available during normal agent work, not only when a user manually launches a separate process.

The extension can eventually:

- register a `memory_inbox_capture` tool callable by agents;
- register slash commands such as `/memory-inbox` and `/memory-candidates`;
- hook `session_before_compact` to capture candidate memories before lossy compaction;
- use `before_agent_start` or prompt guidelines to remind agents how to capture candidates;
- work in normal Pi sessions without requiring a separate subagent orchestration step.

### Why not extension-only

The extension must not contain the only implementation of candidate formatting and capture behavior. Extension-only logic would be hard to test and could drift from CLI behavior.

The extension should be a thin adapter over a deterministic core.

### Why a CLI/library core

The CLI/library core gives us repeatable tests, fixtures, and deterministic evaluation.

The core should provide operations such as:

```text
memory-inbox capture
memory-inbox validate
memory-inbox precompact
```

Later, the Pi extension should call the same core code or CLI operations.

### Why not a subagent

A subagent is not the right primary interface for `memory-inbox` because candidate capture needs to be predictable, always available, and hookable into Pi lifecycle events.

Subagents may help later with:

- analyzing session summaries;
- reviewing candidates;
- suggesting extraction improvements;
- testing adversarial scenarios.

But subagents should not be the memory-inbox runtime itself.

## Operating Modes

For this sandbox, the default MVP posture is `trusted-sandbox`: write candidate records capture-first inside the configured sandbox candidate directory.

| Mode | Behavior | MVP role |
|---|---|---|
| `disabled` | Operational off switch; no candidate writes. | emergency off switch |
| `trusted-sandbox` | YOLO capture-first candidate writing inside explicitly trusted sandbox paths. | default target for this repo |

Other modes such as `manual`, `suggest`, `candidate-write`, or stricter policy-gated modes may be added later if useful, but they are not the MVP posture.

## Product Boundary

`memory-inbox` owns:

- candidate schema;
- candidate capture interface;
- candidate validation;
- sensitivity classification and triage flags;
- permissive capture-first candidate Markdown writing;
- pre-compaction candidate extraction entry point;
- inbox operation audit messages or lightweight logs;
- repeatable self-evaluation scenarios.

`memory-inbox` does **not** own:

- active durable memory promotion;
- candidate deduplication across the full memory corpus;
- Markdown memory consolidation;
- SQLite/vector index rebuilding;
- semantic retrieval;
- profile memory updates;
- procedure/playbook promotion;
- final memory truth.

Those belong to `memory-consolidator` or later memory services.

## Initial Product Success Criteria

The first useful version of `memory-inbox` succeeds if it can:

1. Accept an explicit memory request and create one valid candidate Markdown record.
2. Capture hidden, private, or secret-like synthetic input as a candidate with review metadata instead of rejecting it.
3. Capture a pre-compaction session summary as an `episode` candidate.
4. Preserve enough provenance for a future consolidator to review the candidate.
5. Pass repeatable scenario tests without writing outside the sandbox candidate directory.

## Pi Integration Plan

Event/tool mapping:

| Pi surface | Memory-inbox behavior |
|---|---|
| custom tool | agent calls `memory_inbox_capture` with structured candidate data |
| slash command | human invokes `/memory-inbox` for manual capture/status/review |
| `session_before_compact` | extension invokes `precompact` capture path before lossy compaction |
| optional `before_agent_start` | extension may append guidance telling agents to use candidate capture for durable lessons |

Candidate files should be written to the documented handoff directory:

```text
memory/candidates/
```

## Project-local Adapter Decision

The first Pi integration is project-local:

- `.pi/extensions/memory-inbox/index.ts` registers the Pi tool/command/hook.
- `.pi/extensions/memory-inbox/adapter.py` is a small Python import bridge for tests/future tooling.
- `memory/memory-inbox/src/memory_inbox/pi_adapter.py` contains the adapter functions over the deterministic core.
- `memory/memory-inbox/src/memory_inbox/tracing.py` emits redacted JSONL adapter progress traces.

Adapter traces are generated/disposable artifacts. They are not source of truth and must not include raw captured text or secret-like literals.

## Product Decisions Resolved for MVP

- In this repo, `trusted-sandbox` may be enabled by explicit project config or by the root README sandbox permission.
- In YOLO capture-first mode, preserve secret-like literals verbatim in inbox candidates inside this sandbox. `memory-consolidator` may redact, transform, archive, or reject later.

## Open Questions

- Should pre-compaction candidate extraction call the model, or only capture a structured summary provided by the main agent?
- Should the project-local extension later be packaged globally?
