import { defineExtension } from "@pi-coding-agent/extension-sdk";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ADAPTER = join(__dirname, "adapter.py");

function runAdapter(func: string, ...args: string[]): string {
  const result = spawnSync("python3", ["-c", `
import sys; sys.path.insert(0, '${join(__dirname, "..", "..", "memory", "memory-consolidator", "src")}')
sys.path.insert(0, '${__dirname}')
from adapter import *
import json
result = ${func}(${args.map(a => JSON.stringify(a)).join(", ")})
if isinstance(result, str): print(result)
else: print(json.dumps(result))
`], { encoding: "utf-8", cwd: __dirname });
  return result.stdout || result.stderr || "";
}

export default defineExtension({
  name: "memory-consolidator",
  description: "Gen1 memory consolidator: search, list, get, promote memories",
  tools: [
    {
      name: "memory_consolidator_search",
      description: "Search stored memories by keyword using FTS5 full-text search",
      parameters: {
        type: "object",
        properties: {
          query: { type: "string", description: "Search query (FTS5 syntax)" },
          limit: { type: "integer", default: 10, description: "Max results" },
        },
        required: ["query"],
      },
      handler: (params: { query: string; limit?: number }) =>
        runAdapter("memory_consolidator_search", params.query, String(params.limit || 10)),
    },
    {
      name: "memory_consolidator_list",
      description: "List stored memories with optional type/scope filters",
      parameters: {
        type: "object",
        properties: {
          memory_type: { type: "string", description: "Filter by type (fact, procedure, etc.)" },
          scope: { type: "string", description: "Filter by scope" },
          limit: { type: "integer", default: 20 },
        },
      },
      handler: (params: { memory_type?: string; scope?: string; limit?: number }) =>
        runAdapter("memory_consolidator_list", params.memory_type || "", params.scope || "", String(params.limit || 20)),
    },
    {
      name: "memory_consolidator_get",
      description: "Get a specific memory by its id",
      parameters: {
        type: "object",
        properties: {
          memory_id: { type: "string", description: "Memory id (mem_...)" },
        },
        required: ["memory_id"],
      },
      handler: (params: { memory_id: string }) =>
        runAdapter("memory_consolidator_get", params.memory_id),
    },
    {
      name: "memory_consolidator_promote",
      description: "Promote candidate(s) from memory/candidates/ to stored memories",
      parameters: {
        type: "object",
        properties: {
          candidate_path: { type: "string", description: "Candidate filename or path" },
          all: { type: "boolean", description: "Promote all unprocessed candidates" },
        },
      },
      handler: (params: { candidate_path?: string; all?: boolean }) =>
        runAdapter("memory_consolidator_promote", params.candidate_path || "", String(!!params.all)),
    },
  ],
});
