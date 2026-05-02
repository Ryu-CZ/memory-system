# memory-inbox Pi Extension Bridge

This project-local extension exposes `memory-inbox` to Pi.

## Runtime shape

The extension is intentionally thin:

```text
Pi tool/command/hook
  -> Python adapter / deterministic core
  -> candidate Markdown in memory/candidates/
```

Business logic lives in:

```text
memory/memory-inbox/src/memory_inbox/
```

## Registered Pi surface

`index.ts` registers:

- tool: `memory_inbox_capture`
- command: `/memory-inbox`
- command: `/memory-candidates`
- hook: `session_before_compact`
- status line: `memory-inbox`

## Python bridge

`adapter.py` is a small import bridge for tests or future Python-based tooling. It re-exports:

- `memory_inbox_capture`
- `memory_inbox_precompact`
- `memory_inbox_list`
- `session_before_compact`
- `handle_slash_command`

## Boundaries

The extension must not:

- implement candidate formatting itself;
- call `memory-consolidator`;
- promote active durable memory;
- rebuild indexes;
- create embeddings;
- write outside the project sandbox.

All candidate creation must go through the deterministic `memory_inbox` core.
