#!/usr/bin/env python3
"""Run Level-2 invariants against an arbitrary trace (0% LLM).

Unittest equivalent of the plan's `pytest --trace=...`: point it at any
extracted trace JSON and get a pass/fail report on every W1-W7 invariant.

Usage:
  python3 tests/eval/run_invariants.py path/to/trace.json [path2.json ...]
  EVAL_TRACE=path/to/trace.json python3 -m unittest tests.eval.run_invariants
"""

import json
import os
import sys
import unittest
from pathlib import Path

if __package__ in (None, ""):
    # Allow running as a plain script: python3 tests/eval/run_invariants.py
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tests.eval.invariants import ALL_CHECKS, verify_trace
from tests.eval.schema import from_dict


def _targets():
    cli = [a for a in sys.argv[1:] if a.endswith(".json")]
    if cli:
        return cli
    env = os.environ.get("EVAL_TRACE", "")
    if env:
        return [env]
    return []


def _load_trace(path: str):
    return from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def _report(trace_path: str) -> str:
    trace = _load_trace(trace_path)
    results = verify_trace(trace)
    lines = [f"trace: {trace_path} (type={trace.task_type})"]
    all_clean = True
    for check_id, _fn in ALL_CHECKS:
        violations = results[check_id]
        if violations:
            all_clean = False
            lines.append(f"  FAIL {check_id}:")
            for v in violations:
                lines.append(f"    - {v}")
        else:
            lines.append(f"  ok   {check_id}")
    lines.append("RESULT: " + ("PASS (all invariants hold)" if all_clean else "FAIL"))
    return "\n".join(lines)


def main():
    targets = _targets()
    if not targets:
        print(
            "No trace JSON given. Pass paths as args or set EVAL_TRACE=path.",
            file=sys.stderr,
        )
        print(
            "Example: python3 tests/eval/run_invariants.py tests/eval/fixtures/trace_w4_concurrency.json",
            file=sys.stderr,
        )
        return 2
    failures = 0
    for path in targets:
        text = _report(path)
        print(text)
        print()
        if not text.endswith("PASS (all invariants hold)"):
            failures += 1
    return 1 if failures else 0


class TestEnvVarTraceSelection(unittest.TestCase):
    """EVAL_TRACE env var selects a trace for verification (no pytest --trace)."""

    def test_w4_fixture_passes_via_env(self):
        os.environ["EVAL_TRACE"] = str(
            Path(__file__).parent / "fixtures" / "trace_w4_concurrency.json"
        )
        self.addCleanup(lambda: os.environ.pop("EVAL_TRACE", None))
        text = _report(os.environ["EVAL_TRACE"])
        self.assertIn("RESULT: PASS", text)

    def test_round1_investigate_fails_via_env(self):
        os.environ["EVAL_TRACE"] = str(
            Path(__file__).parent / "fixtures" / "trace_round1_investigate.json"
        )
        self.addCleanup(lambda: os.environ.pop("EVAL_TRACE", None))
        text = _report(os.environ["EVAL_TRACE"])
        self.assertIn("RESULT: FAIL", text)
        self.assertIn("W1", text)


if __name__ == "__main__":
    sys.exit(main())
