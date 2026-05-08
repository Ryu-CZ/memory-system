import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "@earendil-works/pi-ai";
import { spawnSync } from "node:child_process";
import path from "node:path";
import fs from "node:fs";

function repoRoot(): string {
  return path.resolve(__dirname, "..", "..", "..");
}

function inboxRoot(): string {
  return path.join(repoRoot(), "memory", "memory-inbox");
}

function runAdapter(operation: string, payload: Record<string, unknown>): any {
  const root = inboxRoot();
  const env = { ...process.env, PYTHONPATH: path.join(root, "src") };
  const result = spawnSync("python3", ["-m", "memory_inbox.pi_adapter", operation], {
    cwd: root,
    env,
    input: JSON.stringify(payload),
    encoding: "utf8",
    maxBuffer: 1024 * 1024,
  });
  const output = (result.stdout || "").trim();
  if (output) {
    try {
      return JSON.parse(output);
    } catch (error) {
      return { ok: false, status: "error", error_type: "AdapterJsonError", error: String(error), stdout: output, stderr: result.stderr };
    }
  }
  return { ok: false, status: "error", error_type: "AdapterExecutionError", error: result.stderr || `exit ${result.status}` };
}

const CaptureParams = Type.Object({
  text: Type.String({ description: "Text to capture as a memory candidate" }),
  source: Type.Optional(Type.String({ description: "source metadata; default user_explicit" })),
  source_agent: Type.Optional(Type.String({ description: "source agent metadata; default extension:memory-inbox" })),
  memory_type: Type.Optional(Type.String({ description: "memory type; default project_context" })),
  scope: Type.Optional(Type.String({ description: "scope; default project:memory-system" })),
  sensitivity: Type.Optional(Type.String({ description: "sensitivity; default ordinary" })),
  retention: Type.Optional(Type.String({ description: "retention; default session_only" })),
  triage_flags: Type.Optional(Type.Array(Type.String())),
  mode: Type.Optional(Type.String({ description: "disabled or trusted-sandbox" })),
});

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "memory_inbox_capture",
    label: "Memory Inbox Capture",
    description: "Capture text as a YOLO memory-inbox candidate Markdown record. Candidate-only; does not consolidate or promote memory.",
    promptSnippet: "Capture text as a memory-inbox candidate Markdown record",
    promptGuidelines: [
      "Use memory_inbox_capture when the user explicitly asks to remember something, when a durable lesson should survive compaction, or when a TTRPG-style hidden fact should be captured as a candidate.",
      "memory_inbox_capture is YOLO capture-first and candidate-only; it does not promote active memory or call memory-consolidator.",
    ],
    parameters: CaptureParams,
    async execute(_toolCallId, params) {
      const result = runAdapter("capture", params as Record<string, unknown>);
      return {
        content: [{ type: "text", text: result.ok ? `Captured memory candidate: ${result.path}` : `memory-inbox error: ${result.error || result.status}` }],
        details: result,
      };
    },
  });

  pi.registerCommand("memory-inbox", {
    description: "Capture text into memory-inbox, or show status when no text is provided",
    handler: async (args, ctx) => {
      const text = String(args || "").trim();
      const result = text ? runAdapter("capture", { text, source: "user_explicit", source_agent: "user" }) : runAdapter("status", {});
      ctx.ui.notify(result.ok ? JSON.stringify(result, null, 2) : `memory-inbox error: ${result.error || result.status}`, result.ok ? "success" : "error");
    },
  });

  pi.registerCommand("memory-candidates", {
    description: "List memory-inbox candidate records",
    handler: async (_args, ctx) => {
      const result = runAdapter("list", {});
      ctx.ui.notify(result.ok ? JSON.stringify(result, null, 2) : `memory-inbox error: ${result.error || result.status}`, result.ok ? "info" : "error");
    },
  });

  pi.on("session_before_compact", async (event) => {
    const summary = `Pi session_before_compact hook fired. tokensBefore=${event.preparation?.tokensBefore ?? "unknown"}. firstKeptEntryId=${event.preparation?.firstKeptEntryId ?? "unknown"}.`;
    const result = runAdapter("session-before-compact", { summary, source: "agent_summary", source_agent: "extension:memory-inbox" });
    if (!result.ok) {
      return undefined;
    }
    return undefined;
  });

  pi.on("session_start", async (_event, ctx) => {
    const root = inboxRoot();
    const exists = fs.existsSync(path.join(root, "src", "memory_inbox", "pi_adapter.py"));
    ctx.ui.setStatus("memory-inbox", exists ? "memory-inbox ready" : "memory-inbox missing");
  });
}
