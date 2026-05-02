"""Pi extension adapter for memory-consolidator."""
import json, os, sys
from pathlib import Path

_project = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_project / "memory" / "memory-consolidator" / "src"))

from memory_consolidator.consolidator import Consolidator

_DB = _project / "memory" / "memory-consolidator" / "store.db"
_CANDIDATES = _project / "memory" / "candidates"


def memory_consolidator_search(query: str, limit: int = 10) -> str:
    """Search memories by keyword using FTS5."""
    c = Consolidator(_DB, _CANDIDATES)
    try:
        results = c.search(query, limit)
        if not results:
            return "No memories found matching query."
        lines = [f"Found {len(results)} memory(ies):"]
        for m in results:
            lines.append(f"- [{m.memory_type}] {m.title} (id: {m.id})")
            lines.append(f"  scope: {m.scope}, source: {m.source}")
            lines.append(f"  {m.content[:150]}")
        return "\n".join(lines)
    finally:
        c.close()


def memory_consolidator_list(memory_type: str = "", scope: str = "", limit: int = 20) -> str:
    """List memories with optional filters."""
    c = Consolidator(_DB, _CANDIDATES)
    try:
        mems = c.list(
            memory_type=memory_type or None,
            scope=scope or None,
            limit=limit,
        )
        if not mems:
            return "No memories found."
        lines = [f"Found {len(mems)} memory(ies):"]
        for m in mems:
            lines.append(f"- {m.id} [{m.status}] {m.memory_type} {m.title}")
        return "\n".join(lines)
    finally:
        c.close()


def memory_consolidator_get(memory_id: str) -> str:
    """Get a specific memory by id."""
    c = Consolidator(_DB, _CANDIDATES)
    try:
        m = c.get(memory_id)
        return json.dumps(m.to_dict(), indent=2)
    finally:
        c.close()


def memory_consolidator_promote(candidate_path: str = "", all_: bool = False) -> str:
    """Promote candidate(s) from memory/candidates/ to stored memories."""
    c = Consolidator(_DB, _CANDIDATES)
    try:
        if all_:
            mems = c.promote_all()
            return f"Promoted {len(mems)} candidates."
        path = Path(candidate_path)
        if not path.exists():
            path = _CANDIDATES / candidate_path
        if not path.exists():
            return f"Candidate not found: {candidate_path}"
        m = c.promote(path)
        return f"Promoted: {m.id} ({m.title})"
    finally:
        c.close()
