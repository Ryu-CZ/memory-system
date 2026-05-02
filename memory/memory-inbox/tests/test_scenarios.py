import tempfile
import unittest
from pathlib import Path

from memory_inbox.scenarios import run_scenarios


class ScenarioTests(unittest.TestCase):
    def test_all_scenarios_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            scenarios = Path(__file__).parent / "scenarios"
            results = run_scenarios(scenarios, Path(tmp), created_at="2026-04-27T00:00:00Z")
            failures = [result for result in results if not result.ok]
            self.assertEqual(failures, [])
            self.assertEqual(
                [result.scenario_id for result in results],
                [
                    "001-explicit-user-sandbox-permission",
                    "002-secret-like-capture-first",
                    "003-precompaction-session-summary",
                ],
            )


if __name__ == "__main__":
    unittest.main()
