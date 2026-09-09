"""Level 3 probe deterministic-path tests (0% LLM, no API).

Covers the deterministic pre-checks in probes/brief_synthesis.py. The LLM
fallback branches are never exercised here: no EVAL_LLM_API is set in CI, so
every path degrades to a fixed-vocabulary answer or SKIP/NEEDS-LLM without a
network call.
"""

import unittest
from pathlib import Path

from tests.eval.probes.brief_synthesis import (
    probe_behavior_proof,
    probe_brief_restraint,
    probe_dismissal_justification,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _load(name):
    import json

    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class TestProbeBriefRestraint(unittest.TestCase):
    def test_w4_two_children_disjoint(self):
        result = probe_brief_restraint(_load("trace_w4_concurrency.json"))
        self.assertTrue(result.startswith("PASS"), result)

    def test_single_child_skips(self):
        result = probe_brief_restraint(_load("trace_round2_feature.json"))
        self.assertTrue(result.startswith("SKIP"), result)


class TestProbeDismissalJustification(unittest.TestCase):
    def test_no_dismissal_skips(self):
        result = probe_dismissal_justification(_load("trace_round1_feature.json"))
        self.assertTrue(result.startswith("SKIP"), result)


class TestProbeBehaviorProof(unittest.TestCase):
    def test_round2_feature_aligned(self):
        result = probe_behavior_proof(_load("trace_round2_feature.json"))
        self.assertTrue(result.startswith("ALIGNED"), result)

    def test_round1_feature_misaligned(self):
        result = probe_behavior_proof(_load("trace_round1_feature.json"))
        self.assertTrue(result.startswith("MISALIGNED"), result)

    def test_investigation_skips(self):
        result = probe_behavior_proof(_load("trace_round2_investigate.json"))
        self.assertTrue(result.startswith("SKIP"), result)


if __name__ == "__main__":
    unittest.main()
