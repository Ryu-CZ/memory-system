# Scenario 001: Explicit User Sandbox Permission

## Invocation

Tool/command path: `memory-inbox capture`

## Input Text

The user says:

> This sandbox dir is totally owned by you and created for you to play and experiment freely. Use it to make yourself better and enjoy some fun.

## Caller Metadata

```yaml
source: user_explicit
source_agent: main-agent
memory_type: project_context
scope: project:/home/trval/projects/chats/pi_sandbox
sensitivity: ordinary
retention: indefinite
```

## Expected Product Behavior

Create one candidate Markdown record. The candidate should capture the sandbox permission narrowly as project-scoped context, not as a global user preference.
