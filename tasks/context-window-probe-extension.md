# Task: Context Window Probe Extension for Pi

## Problem

Pi uses a **static `contextWindow` value** from `~/.pi/agent/models.json` (or built-in defaults, defaulting to 128K) to decide when to trigger auto-compaction. For local model servers that dynamically calculate context size at runtime (e.g., llama.cpp with `--fit on`), this value is wrong:

- **Configured**: 128,000 (default) or whatever the user sets in `models.json`
- **Actual runtime**: 141,312 tokens (calculated by llama.cpp based on available memory)

This causes pi to compact earlier than necessary, wasting tokens on summarization and losing context prematurely.

## Why This Matters

- `--fit on` in llama.cpp auto-calculates context size on every startup based on available RAM/VRAM
- Ollama, LM Studio, and vLLM also have dynamic or per-session context limits
- The model's trained context (`n_ctx_train`) is the theoretical maximum, not the actual runtime value
- Pi has no mechanism to discover the actual runtime context window from the server

## Solution: `context-window-probe` Pi Extension

A Pi extension that probes the model server on session start and patches the in-memory model's `contextWindow` to match reality.

### Design

1. **On `session_start`**: Detect if the current model uses a local OpenAI-compatible server
2. **Probe the server**: Query server-specific endpoints for actual context size
3. **Patch in-memory**: Mutate `pi.model.contextWindow` to the actual value
4. **Notify**: Show status in footer or via notification

### Server-Specific Probes

| Server | Endpoint | Field | Notes |
|--------|----------|-------|-------|
| **llama.cpp** | `GET /props` | `default_generation_settings.n_ctx` | Actual slot context size |
| **Ollama** | `GET /api/tags` → model details | `model_info.context_length` or `projector_info.context_length` | Varies by Ollama version |
| **LM Studio** | `GET /v1/models` | Check model metadata | May not expose runtime context |
| **vLLM** | `GET /v1/models` | Check model metadata | May expose `max_model_len` |

### Implementation

#### File Structure

```
context-window-probe/
├── package.json
├── index.ts              # Extension entry point
├── src/
│   ├── probe.ts          # Server probe logic (HTTP requests)
│   ├── servers.ts        # Server detection & endpoint configs
│   └── types.ts          # Type definitions
└── README.md
```

#### Core Logic (`index.ts`)

```typescript
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.on("session_start", async (event, ctx) => {
    const model = ctx.model;
    if (!model) return;

    // Only probe local servers (127.0.0.1, localhost, 0.0.0.0)
    const baseUrl = model.baseUrl;
    if (!baseUrl || !isLocalServer(baseUrl)) return;

    try {
      const actualContext = await probeContextWindow(baseUrl, model.api);
      if (actualContext && actualContext !== model.contextWindow) {
        // Patch in-memory model object
        (model as any).contextWindow = actualContext;
        ctx.ui.notify(
          `Context window corrected: ${model.contextWindow.toLocaleString()} → ${actualContext.toLocaleString()} tokens`,
          "info"
        );
        ctx.ui.setStatus("context-probe", `ctx: ${actualContext.toLocaleString()}`);
      }
    } catch (err) {
      // Silent fail — use configured value as fallback
      console.warn(`[context-window-probe] probe failed: ${err}`);
    }
  });
}

function isLocalServer(url: string): boolean {
  try {
    const u = new URL(url);
    return ["127.0.0.1", "localhost", "0.0.0.0", "::1"].includes(u.hostname);
  } catch {
    return false;
  }
}
```

#### Probe Logic (`src/probe.ts`)

```typescript
export async function probeContextWindow(baseUrl: string, api: string): Promise<number | null> {
  // Try llama.cpp /props endpoint first
  if (api === "openai-completions" || api === "openai-responses") {
    // llama.cpp
    const propsResult = await fetchJson(`${baseUrl}/props`);
    if (propsResult?.default_generation_settings?.n_ctx) {
      return propsResult.default_generation_settings.n_ctx;
    }

    // Ollama - check /api/tags for model info
    const tagsResult = await fetchJson(`${baseUrl.replace('/v1', '')}/api/tags`);
    if (tagsResult?.models) {
      for (const m of tagsResult.models) {
        if (m.name && m.details?.params) {
          // Ollama doesn't expose runtime context directly
          // Fall back to model metadata
          return null;
        }
      }
    }

    // vLLM - check /v1/models for max_model_len
    const modelsResult = await fetchJson(`${baseUrl}/v1/models`);
    if (modelsResult?.data) {
      for (const m of modelsResult.data) {
        if (m.id && m.max_model_len) {
          return m.max_model_len;
        }
      }
    }
  }

  return null;
}

async function fetchJson(url: string, timeout = 3000): Promise<any> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  try {
    const res = await fetch(url, { signal: controller.signal });
    if (res.ok) return res.json();
    return null;
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}
```

### Configuration

Optional config in `~/.pi/agent/extensions.json` or via extension settings:

```json
{
  "context-window-probe": {
    "enabled": true,
    "probeTimeout": 3000,
    "servers": ["llama.cpp", "ollama", "lm-studio", "vllm"],
    "fallbackToConfigured": true
  }
}
```

### Edge Cases

1. **Server not ready yet**: 3-second timeout, silent fallback to configured value
2. **Router mode (llama.cpp)**: `/props` returns dummy `n_ctx: 0` — skip in router mode, probe child server instead
3. **Multiple models**: Only probe the active model's server
4. **Non-OpenAI APIs**: Anthropic, Google — skip (they use cloud APIs with known limits)
5. **Context changes mid-session**: Not handled (would require re-probing on model_select)

### Installation

```bash
pi install git:github.com/username/context-window-probe
```

### Why This Belongs as an Extension (Not Core)

- **Server-specific logic**: Each local server has different endpoints; core shouldn't know about llama.cpp internals
- **Opt-in**: Users with cloud models don't need this
- **Safe fallback**: Silent failure means no breakage if probe fails
- **Extensible**: Other server types can be added without pi core changes

### Why This Could Be Useful for Pi Core

A future core feature could auto-probe context window on session start for all local servers. This extension validates the concept and provides a reference implementation.

## Acceptance Criteria

- [ ] Extension probes llama.cpp `/props` endpoint and patches `contextWindow`
- [ ] Extension handles Ollama, vLLM, LM Studio servers
- [ ] Silent fallback when server is unreachable
- [ ] Status notification when context is corrected
- [ ] Works with `--fit on` llama.cpp configurations
- [ ] Does not affect cloud model providers
- [ ] Package builds and installs via `pi install`

## Estimated Effort

- **Complexity**: Low-Medium
- **Time**: 2-4 hours for MVP (llama.cpp support only)
- **Dependencies**: None (uses built-in fetch)
