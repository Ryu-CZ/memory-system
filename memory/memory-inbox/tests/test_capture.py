import tempfile
import unittest
from pathlib import Path

from memory_inbox.capture import capture_candidate
from memory_inbox.markdown import parse_frontmatter


def base_metadata():
    return {
        "source": "user_explicit",
        "source_agent": "main-agent",
        "memory_type": "project_context",
        "scope": "project:/home/trval/projects/chats/pi_sandbox",
        "sensitivity": "ordinary",
        "retention": "indefinite",
        "triage_flags": [],
    }


class CaptureTests(unittest.TestCase):
    def test_capture_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            text = "The sandbox directory is owned by the agent for play and experiments."
            kwargs = dict(candidate_dir=tmp_path, created_at="2026-04-27T00:00:00Z", operation="capture")
            one = capture_candidate(text, base_metadata(), **kwargs)
            two = capture_candidate(text, base_metadata(), **kwargs)
            self.assertEqual(one.candidate_id, two.candidate_id)
            self.assertEqual(one.path.name, two.path.name)
            self.assertEqual(one.markdown, two.markdown)

    def test_secret_like_capture_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = "Remember this deployment token for later: sk-test-1234567890abcdef1234567890abcdef"
            result = capture_candidate(text, base_metadata(), candidate_dir=Path(tmp), created_at="2026-04-27T00:00:00Z")
            frontmatter, body = parse_frontmatter(result.markdown)
            self.assertEqual(frontmatter["status"], "needs_review")
            self.assertEqual(frontmatter["sensitivity"], "secret-prohibited")
            self.assertIn("yolo_capture_first", frontmatter["triage_flags"])
            self.assertIn("sk-test-1234567890abcdef1234567890abcdef", body)


if __name__ == "__main__":
    unittest.main()
