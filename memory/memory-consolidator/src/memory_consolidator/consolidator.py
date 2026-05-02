"""Consolidator core: promote, reject, merge, search, CRUD, rebuild, health."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .database import create_database, log_event, SCHEMA_SQL
from .promoter import SimplePromoter
from .schema import Memory, parse_candidate_file


class Consolidator:
    """Generation 1 consolidator: candidates → SQLite → FTS5 retrieval."""

    def __init__(self, db_path: str | Path, candidates_dir: str | Path | None = None):
        self.db_path = Path(db_path)
        self.candidates_dir = Path(candidates_dir) if candidates_dir else None
        self.conn = create_database(self.db_path)

        self.promoter = SimplePromoter(self.conn)

    def close(self) -> None:
        self.conn.close()

    # ── Promotion ──────────────────────────────────────────────────────

    def promote(self, candidate_path: Path) -> Memory:
        return self.promoter.promote_candidate(candidate_path)

    def promote_all(self, candidates_dir: str | Path | None = None) -> list[Memory]:
        dir_path = Path(candidates_dir or (self.candidates_dir or ""))
        if not dir_path.exists():
            raise FileNotFoundError(f"candidates directory not found: {dir_path}")
        memories: list[Memory] = []
        for f in sorted(dir_path.glob("*.md")):
            try:
                memories.append(self.promote(f))
            except ValueError:
                pass
        return memories

    def reject(self, candidate_id: str, reason: str = "") -> None:
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            "INSERT OR REPLACE INTO candidates_processed (candidate_id, processed_at, action, notes) VALUES (?, ?, 'rejected', ?)",
            (candidate_id, now, reason),
        )
        self.conn.commit()

    def merge(self, candidate_ids: list[str], target_memory_id: str) -> Memory:
        now = datetime.now(timezone.utc).isoformat()
        row = self.conn.execute("SELECT * FROM memories WHERE memory_id = ?", (target_memory_id,)).fetchone()
        if not row:
            raise ValueError(f"target memory {target_memory_id} not found")
        for cid in candidate_ids:
            self.conn.execute(
                "INSERT OR REPLACE INTO candidates_processed (candidate_id, processed_at, action, target_memory_id) VALUES (?, ?, 'merged', ?)",
                (cid, now, target_memory_id),
            )
        log_event(self.conn, target_memory_id, "merged", source_candidate_id=",".join(candidate_ids), event_at=now)
        self.conn.commit()
        return Memory.from_row(dict(row))

    # ── Retrieval ──────────────────────────────────────────────────────

    def search(self, query: str, limit: int = 10) -> list[Memory]:
        rows = self.conn.execute(
            "SELECT memories.* FROM memories JOIN memories_fts ON memories.id = memories_fts.rowid WHERE memories_fts MATCH ? AND memories.status = 'active' ORDER BY bm25(memories_fts) LIMIT ?",
            (query, limit),
        ).fetchall()
        return [Memory.from_row(dict(r)) for r in rows]

    def get(self, memory_id: str) -> Memory:
        row = self.conn.execute("SELECT * FROM memories WHERE memory_id = ?", (memory_id,)).fetchone()
        if not row:
            raise ValueError(f"memory {memory_id} not found")
        return Memory.from_row(dict(row))

    def list(self, memory_type: str | None = None, scope: str | None = None, status: str = "active", limit: int = 100) -> list[Memory]:
        conditions, params = ["status = ?"], [status]
        if memory_type:
            conditions.append("memory_type = ?")
            params.append(memory_type)
        if scope:
            conditions.append("scope = ?")
            params.append(scope)
        params.append(limit)
        rows = self.conn.execute(
            f"SELECT * FROM memories WHERE {' AND '.join(conditions)} ORDER BY promoted_at DESC LIMIT ?",
            params,
        ).fetchall()
        return [Memory.from_row(dict(r)) for r in rows]

    # ── Updates ────────────────────────────────────────────────────────

    def update(self, memory_id: str, **changes: Any) -> Memory:
        allowed = {"title", "content", "memory_type", "scope", "sensitivity", "retention", "tags", "metadata", "confidence", "level"}
        updates = {k: v for k, v in changes.items() if k in allowed}
        if not updates:
            return self.get(memory_id)
        if "tags" in updates:
            updates["tags"] = json.dumps(updates["tags"])
        if "metadata" in updates:
            updates["metadata"] = json.dumps(updates["metadata"])
        now = datetime.now(timezone.utc).isoformat()
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        self.conn.execute(f"UPDATE memories SET {set_clause} WHERE memory_id = ?", list(updates.values()) + [memory_id])
        log_event(self.conn, memory_id, "updated", metadata=dict(updates), event_at=now)
        self.conn.commit()
        return self.get(memory_id)

    def archive(self, memory_id: str) -> Memory:
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute("UPDATE memories SET status = 'archived' WHERE memory_id = ?", (memory_id,))
        log_event(self.conn, memory_id, "archived", event_at=now)
        self.conn.commit()
        return self.get(memory_id)

    def supersede(self, old_id: str, new_id: str) -> Memory:
        old_row = self.conn.execute("SELECT memory_id, derived_from FROM memories WHERE memory_id = ?", (old_id,)).fetchone()
        if not old_row:
            raise ValueError(f"old memory {old_id} not found")
        new_row = self.conn.execute("SELECT memory_id, derived_from FROM memories WHERE memory_id = ?", (new_id,)).fetchone()
        if not new_row:
            raise ValueError(f"new memory {new_id} not found")
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute("UPDATE memories SET status = 'superseded', superseded_by = ? WHERE memory_id = ?", (new_id, old_id))
        existing_derived = json.loads(new_row["derived_from"]) if new_row["derived_from"] and isinstance(new_row["derived_from"], str) else []
        existing_derived.append(old_id)
        self.conn.execute("UPDATE memories SET derived_from = ?, derived_via = 'supersession' WHERE memory_id = ?", (json.dumps(existing_derived), new_id))
        log_event(self.conn, old_id, "superseded", source_memory_id=new_id, event_at=now)
        self.conn.commit()
        return self.get(new_id)

    # ── Rebuild ────────────────────────────────────────────────────────

    def rebuild(self, candidates_dir: str | Path | None = None) -> int:
        dir_path = Path(candidates_dir or (self.candidates_dir or ""))
        if not dir_path.exists():
            raise FileNotFoundError(f"candidates directory not found: {dir_path}")
        self.conn.executescript("DROP TABLE IF EXISTS memory_events; DROP TABLE IF EXISTS candidates_processed; DROP TABLE IF EXISTS memories_fts; DROP TABLE IF EXISTS memories;")
        self.conn.executescript(SCHEMA_SQL)
        self.conn.commit()
        self.promoter = SimplePromoter(self.conn)
        count = 0
        for f in sorted(dir_path.glob("*.md")):
            try:
                self.promote(f)
                count += 1
            except Exception:
                pass
        return count

    # ── Health Check ───────────────────────────────────────────────────

    def health_check(self) -> dict[str, Any]:
        issues: dict[str, list[str]] = {}
        orphans = self.conn.execute(
            "SELECT m.memory_id FROM memories m LEFT JOIN candidates_processed cp ON m.candidate_id = cp.candidate_id WHERE cp.candidate_id IS NULL"
        ).fetchall()
        if orphans:
            issues["orphaned_memories"] = [r["memory_id"] for r in orphans]
        broken = self.conn.execute(
            "SELECT m.memory_id FROM memories m WHERE m.superseded_by IS NOT NULL AND m.superseded_by NOT IN (SELECT memory_id FROM memories)"
        ).fetchall()
        if broken:
            issues["broken_supersession"] = [r["memory_id"] for r in broken]
        if self.candidates_dir and self.candidates_dir.exists():
            processed_ids = {r["candidate_id"] for r in self.conn.execute("SELECT candidate_id FROM candidates_processed").fetchall()}
            stale = []
            for f in self.candidates_dir.glob("*.md"):
                try:
                    cid = parse_candidate_file(f).get("id", "")
                    if cid and cid not in processed_ids:
                        stale.append(f.name)
                except Exception:
                    pass
            if stale:
                issues["stale_candidates"] = stale
        total = self.conn.execute("SELECT COUNT(*) as c FROM memories").fetchone()["c"]
        active = self.conn.execute("SELECT COUNT(*) as c FROM memories WHERE status='active'").fetchone()["c"]
        return {"total_memories": total, "active_memories": active, "issues": issues if issues else None, "healthy": not bool(issues)}
