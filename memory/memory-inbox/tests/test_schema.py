import unittest

from memory_inbox.schema import CandidateMetadata, ValidationError, metadata_from_mapping


class SchemaTests(unittest.TestCase):
    def test_secret_prohibited_normalizes_to_needs_review(self):
        meta = CandidateMetadata(
            source="user_explicit",
            source_agent="main-agent",
            memory_type="project_context",
            scope="project:/tmp/project",
            sensitivity="secret-prohibited",
            retention="indefinite",
            triage_flags=("yolo_capture_first",),
        ).normalized()
        self.assertEqual(meta.status, "needs_review")

    def test_invalid_enum_rejected(self):
        with self.assertRaisesRegex(ValidationError, "invalid source"):
            metadata_from_mapping(
                {
                    "source": "bad",
                    "source_agent": "main-agent",
                    "memory_type": "project_context",
                    "scope": "project:/tmp/project",
                    "sensitivity": "ordinary",
                    "retention": "indefinite",
                }
            )


if __name__ == "__main__":
    unittest.main()
