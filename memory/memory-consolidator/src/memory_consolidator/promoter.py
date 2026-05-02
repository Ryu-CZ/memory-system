"""SimplePromoter: read candidate → create memory record."""

from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import json

from .database import log_event
from .schema import Memory, extract_candidate_content, extract_candidate_title, parse_candidate_file


class SimplePromoter:
    """
    Simple promotion logic:
    - Read candidate markdown
    - Extract metadata from frontmatter
    - Create memory record
    - Record promotion action
    """

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def promote_candidate(self, candidate_path: Path) -> Memory:
        """Promote a single candidate file to a stored memory."""
        data = parse_candidate_file(candidate_path)
        body = data.pop("_body", "")

        candidate_id = data.get("id", "")
        if not candidate_id:
            candidate_id = self._derive_candidate_id(candidate_path.name)

        # Check if already processed
        existing = self.conn.execute(
            "SELECT candidate_id FROM candidates_processed WHERE candidate_id = ?",
            (candidate_id,),
        ).fetchone()
        if existing:
            raise ValueError(f"candidate {candidate_id} already processed")

        title = extract_candidate_title(body)
        content = extract_candidate_content(body)
        now = datetime.now(timezone.utc).isoformat()

        memory_id = self._generate_memory_id(candidate_id, title)

        memory_type = str(data.get("memory_type", "project_context"))
        scope = str(data.get("scope", "global"))
        source = str(data.get("source", "user_explicit"))
        source_agent = str(data.get("source_agent", "")) or None
        sensitivity = str(data.get("sensitivity", "ordinary"))
        retention = str(data.get("retention", "indefinite"))
        created_at = str(data.get("created_at", now))

        triage_flags = data.get("triage_flags", [])
        if isinstance(triage_flags, str):
            triage_flags = [triage_flags]
        tags = list(triage_flags) if triage_flags else []

        metadata = {k: v for k, v in data.items() if k not in (
            "id", "status", "created_at", "source", "source_agent",
            "memory_type", "scope", "sensitivity", "retention", "triage_flags",
        )}

        self.conn.execute(
            "INSERT INTO memories (memory_id, candidate_id, title, content, memory_type, scope, created_at, promoted_at, source, source_agent, sensitivity, retention, tags, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (memory_id, candidate_id, title, content, memory_type, scope, created_at, now, source, source_agent, sensitivity, retention, json.dumps(tags), json.dumps(metadata) if metadata else None),
        )

        # Record in candidates_processed
        self.conn.execute(
            """INSERT INTO candidates_processed
               (candidate_id, processed_at, action, target_memory_id)
               VALUES (?, ?, 'promoted', ?)""",
            (candidate_id, now, memory_id),
        )

        # Log event
        log_event(self.conn, memory_id, "created", source_candidate_id=candidate_id, event_at=now)

        self.conn.commit()

        return Memory(
            id=memory_id,
            candidate_id=candidate_id,
            title=title,
            content=content,
            memory_type=memory_type,
            scope=scope,
            created_at=created_at,
            promoted_at=now,
            source=source,
            source_agent=source_agent,
            sensitivity=sensitivity,
            retention=retention,
            tags=tags,
            metadata=metadata,
        )

    def _generate_memory_id(self, candidate_id: str, title: str) -> str:
        """Generate a deterministic memory id from candidate id + title."""
        raw = f"{candidate_id}:{title}"
        hash_suffix = hashlib.sha256(raw.encode()).hexdigest()[:12]
        return f"mem_{hash_suffix}"

    def _derive_candidate_id(self, filename: str) -> str:
        """Derive candidate id from filename if not in frontmatter."""
        # Filename format: YYYYMMDD-HHMMSS-description-hash.md
        stem = Path(filename).stem
        return f"cand_derived_{stem}"
