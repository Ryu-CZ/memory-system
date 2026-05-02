# Memory Inbox Source

This directory contains the deterministic Python CLI/library core for `memory-inbox`.

## Modules

- `memory_inbox.schema` — candidate metadata enums, normalization, and validation.
- `memory_inbox.markdown` — small YAML-like frontmatter serializer/parser for candidate Markdown.
- `memory_inbox.capture` — YOLO capture-first candidate creation and Markdown file writing.
- `memory_inbox.candidates` — candidate Markdown listing helpers.
- `memory_inbox.scenarios` — repeatable scenario fixture loader/evaluator.
- `memory_inbox.tracing` — redacted JSONL operation trace helper for adapter progress.
- `memory_inbox.pi_adapter` — thin Pi-style adapter over capture/precompact core.
- `memory_inbox.cli` — `memory-inbox` command entry point.

## Boundary

This source tree implements candidate capture only. It must not import or call `memory-consolidator`, write active durable memory, rebuild indexes, create embeddings, or write outside the configured candidate directory.
