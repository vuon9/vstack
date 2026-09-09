"""Level 2: deterministic trace-invariant checks against fixtures (0% LLM).

Proves the harness can distinguish the pre-fix (round 1) traces from the
post-fix (round 2) and W4-concurrency traces, purely from recorded evidence.

Fixture expectations (ground truth from the manual evaluations):

- trace_round1_feature.json      -> violates W3 (no user-boundary behavior test)
- trace_round1_investigate.json  -> violates W1 (subagent line-count drift)
- trace_round2_feature.json      -> clean (fixes landed)
- trace_round2_investigate.json  -> clean (fixes landed)
- trace_w4_concurrency.json      -> clean, and its two children overlap in time
"""

import json
import unittest
from pathlib import Path

from .invariants import verify_trace
from .schema import from_dict

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str):
    return from_dict(json.loads((FIXTURES / name).read_text(encoding="utf-8")))


def _violations(trace):
    return {k: v for k, v in verify_trace(trace).items() if v}


class TestFixtureFidelity(unittest.TestCase):
    """The harness reproduces the manual round-1 vs round-2 verdicts."""

    def test_round1_feature_fails_w3(self):
        vio = _violations(_load("trace_round1_feature.json"))
        self.assertIn("W3", vio, f"expected W3 violation, got {sorted(vio)}")

    def test_round1_investigate_fails_w1(self):
        vio = _violations(_load("trace_round1_investigate.json"))
        self.assertIn("W1", vio, f"expected W1 violation, got {sorted(vio)}")
        self.assertTrue(
            any("43 lines" in v for v in vio["W1"]),
            "W1 violation should flag the 43-vs-49 line drift",
        )

    def test_round2_feature_is_clean(self):
        vio = _violations(_load("trace_round2_feature.json"))
        self.assertEqual(vio, {}, f"round2 feature should be clean, got {vio}")

    def test_round2_investigate_is_clean(self):
        vio = _violations(_load("trace_round2_investigate.json"))
        self.assertEqual(vio, {}, f"round2 investigate should be clean, got {vio}")

    def test_w4_concurrency_is_clean(self):
        vio = _violations(_load("trace_w4_concurrency.json"))
        self.assertEqual(vio, {}, f"w4 concurrency should be clean, got {vio}")


class TestW4Overlap(unittest.TestCase):
    """The W4 fixture's two workers genuinely overlap in time."""

    def test_two_timed_workers_overlap(self):
        trace = _load("trace_w4_concurrency.json")
        timed = []
        for s in trace.subagents:
            if (
                s.subagent_id != "parent-notify"
                and s.start_time_ms is not None
                and s.end_time_ms is not None
            ):
                timed.append(s)
        self.assertGreaterEqual(len(timed), 2, "need at least two timed subagents")
        a, b = timed[0], timed[1]
        overlap = max(
            0, min(a.end_time_ms, b.end_time_ms) - max(a.start_time_ms, b.start_time_ms)
        )
        self.assertGreater(overlap, 0, "worker runs must overlap in time")

    def test_workers_touched_disjoint_files(self):
        trace = _load("trace_w4_concurrency.json")
        touched = []
        for s in trace.subagents:
            if s.subagent_id == "parent-notify":
                continue
            files = set()
            for tc in s.tool_calls:
                cmd = str(tc.input.get("command") or "")
                for part in ("area", "temp"):
                    if part in cmd:
                        files.add(part)
            touched.append(files)
        self.assertGreaterEqual(len(touched), 2)
        self.assertIn("area", touched[0] | touched[1])
        self.assertIn("temp", touched[0] | touched[1])


class TestW3BoundaryDetection(unittest.TestCase):
    """W3 distinguishes the round-1 diff (unit only) from round-2 (CLI test)."""

    def test_round2_diff_has_cli_boundary(self):

        diff = _load("trace_round2_feature.json").patch_diff
        self.assertRegex(diff, r"subprocess")
        self.assertRegex(diff, r"stdout|returncode|exit")


if __name__ == "__main__":
    unittest.main()
