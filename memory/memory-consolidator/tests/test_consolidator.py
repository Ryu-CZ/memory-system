"""Tests for memory-consolidator Gen1."""
from __future__ import annotations
import json, os, sqlite3, tempfile, unittest, sys
from pathlib import Path

_project_root = Path(__file__).resolve().parents[3]
_src = _project_root / "memory" / "memory-consolidator" / "src"
sys.path.insert(0, str(_src))

from memory_consolidator.consolidator import Consolidator
from memory_consolidator.schema import Memory, parse_candidate_file, extract_candidate_title, extract_candidate_content
from memory_consolidator.promoter import SimplePromoter
from memory_consolidator.database import create_database

FIXTURES = Path(__file__).parent / "fixtures"


class TestSchema(unittest.TestCase):
    def test_parse_candidate_file(self):
        data = parse_candidate_file(FIXTURES / "test-candidate.md")
        self.assertEqual(data["id"], "cand_20260503_120000_abc123")
        self.assertEqual(data["memory_type"], "project_context")

    def test_extract_title(self):
        self.assertEqual(extract_candidate_title("# My Title\n\nContent"), "My Title")

    def test_extract_title_fallback(self):
        self.assertEqual(extract_candidate_title("no heading"), "Untitled candidate")

    def test_extract_content(self):
        body = "## Proposed Memory\n\nThe content.\n\n## Evidence\n\nProof."
        self.assertEqual(extract_candidate_content(body), "The content.")

    def test_memory_from_row(self):
        row = {"memory_id": "m1", "candidate_id": "c1", "title": "T", "content": "C",
               "memory_type": "fact", "scope": "global", "status": "active",
               "created_at": "2026-01-01T00:00:00Z", "promoted_at": "2026-01-01T00:00:00Z",
               "source": "user_explicit", "source_agent": "main", "sensitivity": "ordinary",
               "retention": "indefinite", "tags": '["a"]', "metadata": "{}",
               "superseded_by": None, "derived_from": None, "derived_via": None,
               "confidence": 1.0, "level": 0}
        m = Memory.from_row(row)
        self.assertEqual(m.id, "m1")
        self.assertEqual(m.tags, ["a"])

    def test_from_row_malformed_json(self):
        row = {"memory_id": "m1", "candidate_id": "c1", "title": "T", "content": "C",
               "memory_type": "fact", "scope": "global", "status": "active",
               "created_at": "2026-01-01T00:00:00Z", "promoted_at": "2026-01-01T00:00:00Z",
               "source": "user_explicit", "source_agent": "main", "sensitivity": "ordinary",
               "retention": "indefinite", "tags": "NOT VALID JSON{{{", "metadata": "also bad",
               "superseded_by": None, "derived_from": "broken", "derived_via": None,
               "confidence": 1.0, "level": 0}
        m = Memory.from_row(row)
        self.assertEqual(m.tags, [])
        self.assertEqual(m.metadata, {})
        self.assertEqual(m.derived_from, [])


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
    def tearDown(self):
        os.unlink(self.tmp.name)
    def test_create_database(self):
        conn = create_database(self.tmp.name)
        names = [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        self.assertIn("memories", names)
        self.assertIn("candidates_processed", names)
        self.assertIn("memory_events", names)
        conn.close()
    def test_fts_table(self):
        conn = create_database(self.tmp.name)
        names = [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type IN ('table','shadowtable')").fetchall()]
        self.assertIn("memories_fts", names)
        conn.close()


class TestPromoter(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.conn = create_database(self.tmp.name)
        self.promoter = SimplePromoter(self.conn)
    def tearDown(self):
        self.conn.close()
        os.unlink(self.tmp.name)
    def test_promote(self):
        mem = self.promoter.promote_candidate(FIXTURES / "test-candidate.md")
        self.assertIsInstance(mem, Memory)
        self.assertEqual(mem.candidate_id, "cand_20260503_120000_abc123")
    def test_duplicate_raises(self):
        self.promoter.promote_candidate(FIXTURES / "test-candidate.md")
        with self.assertRaises(ValueError):
            self.promoter.promote_candidate(FIXTURES / "test-candidate.md")
    def test_records_processed(self):
        self.promoter.promote_candidate(FIXTURES / "test-candidate.md")
        row = self.conn.execute("SELECT * FROM candidates_processed WHERE candidate_id=?", ("cand_20260503_120000_abc123",)).fetchone()
        self.assertEqual(row["action"], "promoted")
    def test_creates_event(self):
        self.promoter.promote_candidate(FIXTURES / "test-candidate.md")
        self.assertGreater(len(self.conn.execute("SELECT * FROM memory_events").fetchall()), 0)


class TestConsolidator(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.c = Consolidator(self.tmp.name)
    def tearDown(self):
        self.c.close()
        os.unlink(self.tmp.name)
    def test_promote(self):
        mem = self.c.promote(FIXTURES / "test-candidate.md")
        self.assertTrue(mem.id.startswith("mem_"))
    def test_promote_all(self):
        self.assertEqual(len(self.c.promote_all(FIXTURES)), 2)
    def test_reject(self):
        self.c.reject("cand_test", "reason")
        self.assertEqual(self.c.conn.execute("SELECT action FROM candidates_processed WHERE candidate_id=?", ("cand_test",)).fetchone()["action"], "rejected")
    def test_search(self):
        self.c.promote(FIXTURES / "test-candidate.md")
        self.c.promote(FIXTURES / "test-candidate-2.md")
        self.assertGreaterEqual(len(self.c.search("test")), 1)
    def test_search_empty(self):
        self.assertEqual(len(self.c.search("xyz123nonexistent")), 0)
    def test_get(self):
        mem = self.c.promote(FIXTURES / "test-candidate.md")
        self.assertEqual(self.c.get(mem.id).id, mem.id)
    def test_get_missing(self):
        with self.assertRaises(ValueError):
            self.c.get("nope")
    def test_list(self):
        self.c.promote(FIXTURES / "test-candidate.md")
        self.c.promote(FIXTURES / "test-candidate-2.md")
        self.assertEqual(len(self.c.list()), 2)
    def test_list_filter(self):
        self.c.promote(FIXTURES / "test-candidate.md")
        self.c.promote(FIXTURES / "test-candidate-2.md")
        self.assertEqual(len(self.c.list(memory_type="project_context")), 1)
    def test_update(self):
        mem = self.c.promote(FIXTURES / "test-candidate.md")
        self.assertEqual(self.c.update(mem.id, title="New").title, "New")
    def test_archive(self):
        mem = self.c.promote(FIXTURES / "test-candidate.md")
        self.assertEqual(self.c.archive(mem.id).status, "archived")
    def test_supersede(self):
        m1 = self.c.promote(FIXTURES / "test-candidate.md")
        m2 = self.c.promote(FIXTURES / "test-candidate-2.md")
        self.c.supersede(m1.id, m2.id)
        old = self.c.get(m1.id)
        self.assertEqual(old.status, "superseded")
        self.assertEqual(old.superseded_by, m2.id)
    def test_supersede_bogus_new_id(self):
        m1 = self.c.promote(FIXTURES / "test-candidate.md")
        with self.assertRaises(ValueError):
            self.c.supersede(m1.id, "nonexistent_mem_id")
    def test_health(self):
        self.c.promote(FIXTURES / "test-candidate.md")
        r = self.c.health_check()
        self.assertTrue(r["healthy"])
        self.assertEqual(r["total_memories"], 1)
    def test_rebuild(self):
        self.c.promote(FIXTURES / "test-candidate.md")
        self.assertEqual(self.c.rebuild(FIXTURES), 2)
    def test_merge(self):
        m1 = self.c.promote(FIXTURES / "test-candidate.md")
        m2 = self.c.promote(FIXTURES / "test-candidate-2.md")
        self.assertEqual(self.c.merge([m2.candidate_id], m1.id).id, m1.id)
    def test_merge_missing(self):
        with self.assertRaises(ValueError):
            self.c.merge(["c"], "nope")


if __name__ == "__main__":
    unittest.main()
