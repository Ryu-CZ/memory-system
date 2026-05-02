import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from memory_inbox.pi_adapter import memory_inbox_capture, memory_inbox_list, session_before_compact

TOKEN = "sk-test-1234567890abcdef1234567890abcdef"
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class PiAdapterTests(unittest.TestCase):
    def temp_payload(self, tmp: Path, text: str) -> dict[str, object]:
        return {
            "text": text,
            "source": "user_explicit",
            "source_agent": "main-agent",
            "memory_type": "project_context",
            "scope": "project:/home/trval/projects/chats/pi_sandbox",
            "sensitivity": "ordinary",
            "retention": "indefinite",
            "created_at": "2026-04-27T00:00:00Z",
            "candidate_dir": str(tmp / "candidates"),
            "trace_file": str(tmp / "trace.jsonl"),
        }

    def test_capture_adapter_writes_candidate(self):
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT / "memory" / "memory-inbox" / ".tmp") as tmp_name:
            tmp = Path(tmp_name)
            result = memory_inbox_capture(self.temp_payload(tmp, "This sandbox directory is owned by the agent for experiments."))
            self.assertTrue(result["ok"], result)
            self.assertTrue(Path(result["path"]).exists())
            self.assertEqual(result["frontmatter"]["status"], "candidate")

    def test_session_before_compact_writes_episode_candidate(self):
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT / "memory" / "memory-inbox" / ".tmp") as tmp_name:
            tmp = Path(tmp_name)
            result = session_before_compact(
                {
                    "summary": "Pre-compaction summary for memory-inbox.",
                    "created_at": "2026-04-27T00:00:00Z",
                    "candidate_dir": str(tmp / "candidates"),
                    "trace_file": str(tmp / "trace.jsonl"),
                }
            )
            self.assertTrue(result["ok"], result)
            self.assertEqual(result["frontmatter"]["memory_type"], "episode")
            self.assertIn("pre_compaction_capture", result["frontmatter"]["triage_flags"])

    def test_disabled_mode_writes_no_candidate_but_traces(self):
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT / "memory" / "memory-inbox" / ".tmp") as tmp_name:
            tmp = Path(tmp_name)
            payload = self.temp_payload(tmp, "do not write")
            payload["mode"] = "disabled"
            result = memory_inbox_capture(payload)
            self.assertFalse(result["ok"])
            self.assertEqual(result["status"], "disabled")
            self.assertFalse((tmp / "candidates").exists())
            self.assertTrue((tmp / "trace.jsonl").exists())

    def test_secret_like_literal_is_not_in_trace(self):
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT / "memory" / "memory-inbox" / ".tmp") as tmp_name:
            tmp = Path(tmp_name)
            result = memory_inbox_capture(self.temp_payload(tmp, f"Remember this deployment token for later: {TOKEN}"))
            self.assertTrue(result["ok"], result)
            candidate_text = Path(result["path"]).read_text(encoding="utf-8")
            trace_text = (tmp / "trace.jsonl").read_text(encoding="utf-8")
            self.assertIn(TOKEN, candidate_text)
            self.assertNotIn(TOKEN, trace_text)
            self.assertIn("secret-prohibited", trace_text)

    def test_candidate_dir_outside_project_is_rejected(self):
        result = memory_inbox_capture(
            {
                "text": "outside path test",
                "candidate_dir": "/tmp/outside-memory-inbox-test",
                "trace_file": str(PROJECT_ROOT / "memory" / "memory-inbox" / ".tmp" / "outside-trace.jsonl"),
            }
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error_type"], "ValidationError")

    def test_list_adapter_lists_candidates(self):
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT / "memory" / "memory-inbox" / ".tmp") as tmp_name:
            tmp = Path(tmp_name)
            capture = memory_inbox_capture(self.temp_payload(tmp, "This sandbox directory is owned by the agent for experiments."))
            self.assertTrue(capture["ok"], capture)
            listed = memory_inbox_list({"candidate_dir": str(tmp / "candidates"), "trace_file": str(tmp / "trace.jsonl")})
            self.assertTrue(listed["ok"], listed)
            self.assertEqual(listed["count"], 1)
            self.assertEqual(listed["candidates"][0]["id"], capture["candidate_id"])

    def test_project_local_bridge_imports(self):
        adapter_path = PROJECT_ROOT / ".pi" / "extensions" / "memory-inbox" / "adapter.py"
        spec = importlib.util.spec_from_file_location("memory_inbox_local_adapter", adapter_path)
        self.assertIsNotNone(spec)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertTrue(callable(mod.memory_inbox_capture))
        self.assertTrue(callable(mod.memory_inbox_list))
        self.assertTrue(callable(mod.session_before_compact))


if __name__ == "__main__":
    unittest.main()
