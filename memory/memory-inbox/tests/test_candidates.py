import tempfile
import unittest
from pathlib import Path

from memory_inbox.candidates import list_candidates
from memory_inbox.capture import capture_candidate


class CandidateListTests(unittest.TestCase):
    def test_list_candidates(self):
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp = Path(tmp_name)
            capture_candidate(
                "The sandbox directory is owned by the agent for experiments.",
                {
                    "source": "user_explicit",
                    "source_agent": "main-agent",
                    "memory_type": "project_context",
                    "scope": "project:/home/trval/projects/chats/pi_sandbox",
                    "sensitivity": "ordinary",
                    "retention": "indefinite",
                    "triage_flags": [],
                },
                candidate_dir=tmp,
                created_at="2026-04-27T00:00:00Z",
            )
            summaries = list_candidates(tmp)
            self.assertEqual(len(summaries), 1)
            self.assertEqual(summaries[0].frontmatter["status"], "candidate")


if __name__ == "__main__":
    unittest.main()
