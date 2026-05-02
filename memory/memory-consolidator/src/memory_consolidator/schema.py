"""Memory dataclass and candidate parsing utilities."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _safe_json_loads(value, default):
    """Safely parse JSON string, returning default on failure."""
    if not value or not isinstance(value, str):
        return default
    try:
        return json.loads(value)
    except (json.JSONDecodeError, ValueError):
        return default


@dataclass
class Memory:
    """A promoted, durable memory stored in the consolidator database."""

    id: str
    candidate_id: str
    title: str
    content: str
    memory_type: str
    scope: str
    status: str = "active"
    created_at: str = ""
    promoted_at: str = ""
    source: str = ""
    source_agent: str | None = None
    sensitivity: str = "ordinary"
    retention: str = "indefinite"
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    superseded_by: str | None = None
    derived_from: list[str] = field(default_factory=list)
    derived_via: str | None = None
    confidence: float = 1.0
    level: int = 0

    @classmethod
    def from_row(cls, row: dict) -> "Memory":
        """Construct a Memory from a sqlite3.Row dict."""
        tags_raw = row.get("tags")
        tags = _safe_json_loads(tags_raw, [])
        meta_raw = row.get("metadata")
        meta = _safe_json_loads(meta_raw, {})
        derived_raw = row.get("derived_from")
        derived = _safe_json_loads(derived_raw, [])
        return cls(
            id=row["memory_id"],
            candidate_id=row["candidate_id"],
            title=row["title"],
            content=row["content"],
            memory_type=row["memory_type"],
            scope=row["scope"],
            status=row["status"],
            created_at=row["created_at"],
            promoted_at=row["promoted_at"],
            source=row["source"],
            source_agent=row.get("source_agent"),
            sensitivity=row.get("sensitivity", "ordinary"),
            retention=row.get("retention", "indefinite"),
            tags=tags,
            metadata=meta,
            superseded_by=row.get("superseded_by"),
            derived_from=derived,
            derived_via=row.get("derived_via"),
            confidence=float(row.get("confidence", 1.0)),
            level=int(row.get("level", 0)),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict."""
        return {
            "id": self.id,
            "candidate_id": self.candidate_id,
            "title": self.title,
            "content": self.content,
            "memory_type": self.memory_type,
            "scope": self.scope,
            "status": self.status,
            "created_at": self.created_at,
            "promoted_at": self.promoted_at,
            "source": self.source,
            "source_agent": self.source_agent,
            "sensitivity": self.sensitivity,
            "retention": self.retention,
            "tags": self.tags,
            "metadata": self.metadata,
            "superseded_by": self.superseded_by,
            "derived_from": self.derived_from,
            "derived_via": self.derived_via,
            "confidence": self.confidence,
            "level": self.level,
        }


def parse_candidate_file(path: Path) -> dict[str, Any]:
    """Parse a candidate Markdown file and return frontmatter + body."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"candidate {path.name} missing frontmatter header")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError(f"candidate {path.name} frontmatter not closed")
    raw = text[4:end].strip("\n")
    body = text[end + 4:].lstrip("\n")
    frontmatter = _parse_simple_yaml(raw)
    frontmatter["_body"] = body
    return frontmatter


def _parse_simple_yaml(raw: str) -> dict[str, Any]:
    """Minimal YAML parser for candidate frontmatter (key: value + lists)."""
    data: dict[str, Any] = {}
    current_key: str | None = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - "):
            if current_key is None:
                continue
            data.setdefault(current_key, []).append(line[4:].strip())
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        if value == "[]":
            data[key] = []
        elif value == "null":
            data[key] = None
        elif value == "":
            data[key] = []
        else:
            data[key] = value
    return data


def extract_candidate_title(body: str) -> str:
    """Extract the title from candidate Markdown body (first # heading)."""
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return "Untitled candidate"


def extract_candidate_content(body: str) -> str:
    """Extract the proposed memory content from candidate body.

    Returns text under '## Proposed Memory' through '## Evidence', or full body.
    """
    lines = body.splitlines()
    in_proposed = False
    content_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == "## Proposed Memory":
            in_proposed = True
            continue
        if in_proposed and stripped == "## Evidence":
            break
        if in_proposed and stripped == "## Expected Future Use":
            break
        if in_proposed:
            content_lines.append(line)
    if content_lines:
        return "\n".join(content_lines).strip()
    return body.strip()
