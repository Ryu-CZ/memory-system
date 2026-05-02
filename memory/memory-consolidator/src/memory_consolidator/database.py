"""SQLite database setup with FTS5 full-text search index."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Literal

import json
from datetime import datetime, timezone

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id TEXT UNIQUE NOT NULL,
    candidate_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    memory_type TEXT NOT NULL,
    scope TEXT NOT NULL,
    level INTEGER DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    promoted_at TEXT NOT NULL,
    source TEXT NOT NULL,
    source_agent TEXT,
    sensitivity TEXT DEFAULT 'ordinary',
    retention TEXT DEFAULT 'indefinite',
    tags TEXT,
    metadata TEXT,
    superseded_by TEXT,
    derived_from TEXT,
    derived_via TEXT,
    confidence REAL DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS candidates_processed (
    candidate_id TEXT PRIMARY KEY,
    processed_at TEXT NOT NULL,
    action TEXT NOT NULL,
    target_memory_id TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS memory_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_at TEXT NOT NULL,
    source_candidate_id TEXT,
    source_memory_id TEXT,
    metadata TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
    title, content, tags, scope, memory_type,
    content=memories,
    content_rowid=id
);

CREATE TRIGGER IF NOT EXISTS memories_fts_insert AFTER INSERT ON memories
BEGIN
    INSERT INTO memories_fts(rowid, title, content, tags, scope, memory_type)
    VALUES (new.id, new.title, new.content, new.tags, new.scope, new.memory_type);
END;

CREATE TRIGGER IF NOT EXISTS memories_fts_delete AFTER DELETE ON memories
BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, title, content, tags, scope, memory_type)
    VALUES ('delete', old.id, old.title, old.content, old.tags, old.scope, old.memory_type);
END;

CREATE TRIGGER IF NOT EXISTS memories_fts_update AFTER UPDATE ON memories
BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, title, content, tags, scope, memory_type)
    VALUES ('delete', old.id, old.title, old.content, old.tags, old.scope, old.memory_type);
    INSERT INTO memories_fts(rowid, title, content, tags, scope, memory_type)
    VALUES (new.id, new.title, new.content, new.tags, new.scope, new.memory_type);
END;

CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_memories_scope ON memories(scope);
CREATE INDEX IF NOT EXISTS idx_memories_status ON memories(status);
CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at);
CREATE INDEX IF NOT EXISTS idx_memories_candidate ON memories(candidate_id);
"""


def create_database(db_path: str | Path) -> sqlite3.Connection:
    """Create (or open) the SQLite database and apply schema."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def log_event(
    conn: sqlite3.Connection,
    memory_id: str,
    event_type: Literal["created", "updated", "archived", "superseded", "merged"],
    *,
    source_candidate_id: str | None = None,
    source_memory_id: str | None = None,
    metadata: dict | None = None,
    event_at: str | None = None,
) -> None:
    """Insert a memory event into the event log."""
    if event_at is None:
        event_at = datetime.now(timezone.utc).isoformat()
    metadata_json = json.dumps(metadata) if metadata else None
    conn.execute(
        "INSERT INTO memory_events (memory_id, event_type, event_at, source_candidate_id, source_memory_id, metadata) VALUES (?, ?, ?, ?, ?, ?)",
        (memory_id, event_type, event_at, source_candidate_id, source_memory_id, metadata_json),
    )
