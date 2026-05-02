from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .candidates import list_candidates
from .capture import capture_candidate, validate_candidate_markdown
from .schema import ValidationError, metadata_from_mapping
from .tracing import append_trace_event

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_CANDIDATE_DIR = PROJECT_ROOT / "memory" / "candidates"
DEFAULT_TRACE_FILE = PROJECT_ROOT / "memory" / "memory-inbox" / ".tmp" / "pi-adapter" / "trace.jsonl"


def resolve_project_path(value: str | None, default: Path) -> Path:
    if not value:
        return default
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    resolved = path.resolve()
    project = PROJECT_ROOT.resolve()
    if resolved != project and project not in resolved.parents:
        raise ValidationError(f"path must stay inside project root: {value}")
    return resolved


def metadata_from_payload(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    flags = list(payload.get("triage_flags") or [])
    if isinstance(payload.get("triage_flags"), str):
        flags = [str(payload["triage_flags"])]
    if operation == "precompact" and "pre_compaction_capture" not in flags:
        flags.append("pre_compaction_capture")
    return {
        "source": payload.get("source") or ("agent_summary" if operation == "precompact" else "user_explicit"),
        "source_agent": payload.get("source_agent") or "extension:memory-inbox",
        "memory_type": payload.get("memory_type") or ("episode" if operation == "precompact" else "project_context"),
        "scope": payload.get("scope") or "project:/home/trval/projects/chats/pi_sandbox",
        "sensitivity": payload.get("sensitivity") or "ordinary",
        "retention": payload.get("retention") or ("review_by" if operation == "precompact" else "session_only"),
        "triage_flags": flags,
    }


def success_response(operation: str, result: Any, trace_path: Path) -> dict[str, Any]:
    validate_candidate_markdown(result.path)
    return {
        "ok": True,
        "status": "success",
        "operation": operation,
        "candidate_id": result.candidate_id,
        "path": str(result.path),
        "frontmatter": result.frontmatter,
        "validated": True,
        "trace_path": str(trace_path),
    }


def write_trace(payload: dict[str, Any], event: dict[str, Any]) -> Path:
    trace_file = resolve_project_path(str(payload["trace_file"]), DEFAULT_TRACE_FILE) if payload.get("trace_file") else DEFAULT_TRACE_FILE
    return append_trace_event({"adapter": "memory-inbox", **event}, trace_file=trace_file)


def run_capture(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    if payload.get("mode") == "disabled":
        trace_path = write_trace(payload, {"operation": operation, "status": "disabled"})
        return {"ok": False, "status": "disabled", "operation": operation, "trace_path": str(trace_path)}
    text = str(payload.get("summary") or payload.get("text") or "").strip()
    if not text:
        raise ValidationError("payload requires text or summary")
    metadata = metadata_from_mapping(metadata_from_payload(payload, operation=operation))
    candidate_dir = resolve_project_path(str(payload["candidate_dir"]), DEFAULT_CANDIDATE_DIR) if payload.get("candidate_dir") else DEFAULT_CANDIDATE_DIR
    result = capture_candidate(
        text,
        metadata,
        candidate_dir=candidate_dir,
        created_at=str(payload["created_at"]) if payload.get("created_at") else None,
        operation=operation,
    )
    trace_path = write_trace(
        payload,
        {
            "operation": operation,
            "status": "success",
            "candidate_id": result.candidate_id,
            "path": str(result.path),
            "source": result.frontmatter.get("source"),
            "source_agent": result.frontmatter.get("source_agent"),
            "memory_type": result.frontmatter.get("memory_type"),
            "scope": result.frontmatter.get("scope"),
            "sensitivity": result.frontmatter.get("sensitivity"),
            "retention": result.frontmatter.get("retention"),
            "triage_flags": result.frontmatter.get("triage_flags"),
        },
    )
    return success_response(operation, result, trace_path)


def memory_inbox_capture(payload: dict[str, Any]) -> dict[str, Any]:
    return safe_adapter_call(payload, operation="capture")


def memory_inbox_precompact(payload: dict[str, Any]) -> dict[str, Any]:
    return safe_adapter_call(payload, operation="precompact")


def session_before_compact(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary") or payload.get("text")
    if not summary:
        summary = "Pi session_before_compact hook fired; capture this pre-compaction event as an episode candidate."
    next_payload = {**payload, "summary": summary}
    return memory_inbox_precompact(next_payload)


def memory_inbox_list(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = dict(payload or {})
    try:
        candidate_dir = resolve_project_path(str(data["candidate_dir"]), DEFAULT_CANDIDATE_DIR) if data.get("candidate_dir") else DEFAULT_CANDIDATE_DIR
        candidates = [summary.as_dict() for summary in list_candidates(candidate_dir)]
        trace_path = write_trace(data, {"operation": "list", "status": "success", "count": len(candidates)})
        return {"ok": True, "status": "success", "operation": "list", "count": len(candidates), "candidates": candidates, "trace_path": str(trace_path)}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "status": "error", "operation": "list", "error_type": type(exc).__name__, "error": str(exc)}


def handle_slash_command(command: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = dict(payload or {})
    if command in {"capture", "memory-inbox"}:
        return memory_inbox_capture(data)
    if command in {"precompact", "memory-inbox-precompact"}:
        return memory_inbox_precompact(data)
    if command in {"list", "memory-candidates"}:
        return memory_inbox_list(data)
    if command in {"status", "memory-inbox-status"}:
        return {"ok": True, "status": "ready", "candidate_dir": str(DEFAULT_CANDIDATE_DIR), "trace_file": str(DEFAULT_TRACE_FILE)}
    return {"ok": False, "status": "error", "error_type": "UnknownCommand", "error": command}


def safe_adapter_call(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    try:
        return run_capture(payload, operation=operation)
    except Exception as exc:  # noqa: BLE001 - adapter boundary returns structured errors.
        event = {
            "operation": operation,
            "status": "error",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "source": payload.get("source"),
            "source_agent": payload.get("source_agent"),
            "memory_type": payload.get("memory_type"),
            "scope": payload.get("scope"),
            "sensitivity": payload.get("sensitivity"),
            "retention": payload.get("retention"),
            "triage_flags": payload.get("triage_flags"),
        }
        try:
            trace_path = write_trace(payload, event)
            trace_str = str(trace_path)
        except Exception:
            trace_str = ""
        return {"ok": False, "status": "error", "operation": operation, "error_type": type(exc).__name__, "error": str(exc), "trace_path": trace_str}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    operation = args[0] if args else "capture"
    payload = json.loads(sys.stdin.read() or "{}")
    if operation == "capture":
        result = memory_inbox_capture(payload)
    elif operation in {"precompact", "session-before-compact"}:
        result = memory_inbox_precompact(payload) if operation == "precompact" else session_before_compact(payload)
    elif operation == "list":
        result = memory_inbox_list(payload)
    elif operation == "status":
        result = handle_slash_command("status", payload)
    else:
        result = {"ok": False, "status": "error", "error_type": "UnknownOperation", "error": operation}
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
