from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SECRET_LIKE_RE = re.compile(r"\b(?:sk|pk|ghp|gho|xoxb|AKIA|token)[-_A-Za-z0-9]{12,}\b")

SENSITIVE_KEYS = {"text", "summary", "markdown", "body", "proposed_memory", "evidence", "input"}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_trace_file() -> Path:
    return Path(__file__).resolve().parents[2] / ".tmp" / "pi-adapter" / "trace.jsonl"


def redact_string(value: str) -> str:
    return SECRET_LIKE_RE.sub("[REDACTED_SECRET_LIKE_LITERAL]", value)


def redact_trace_value(value: Any, *, key: str | None = None) -> Any:
    if key in SENSITIVE_KEYS:
        return "[REDACTED]"
    if isinstance(value, str):
        return redact_string(value)
    if isinstance(value, list):
        return [redact_trace_value(item) for item in value]
    if isinstance(value, dict):
        return {str(k): redact_trace_value(v, key=str(k)) for k, v in value.items()}
    return value


def append_trace_event(event: dict[str, Any], trace_file: Path | None = None) -> Path:
    path = (trace_file or default_trace_file()).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    clean = redact_trace_value({"timestamp": now_utc(), **event})
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(clean, sort_keys=True) + "\n")
    return path
