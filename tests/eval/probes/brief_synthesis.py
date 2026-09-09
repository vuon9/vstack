"""Level 3: targeted semantic probes (opt-in, minimal LLM).

The plan (docs/eval/vmode-eval-systematic-plan.md) allows <20% LLM only where
deterministic parsing is insufficient, and routes the semantic turn through
a cheap contributor-tier model (opencode/muse-spark-1.2-contributor-free in
CI). These probes are NOT auto-run by unittest discovery (no test_ prefix, no
default case) so CI stays 0-LLM; the deterministic pre-checks run first and
the LLM branch only fires when EVAL_LLM_API / EVAL_LLM_MODEL are set.

Run explicitly:

  python3 tests/eval/probes/brief_synthesis.py <trace.json> \
      --probe brief-restraint
  python3 tests/eval/probes/brief_synthesis.py <trace.json> \
      --probe dismissal-justification
  python3 tests/eval/probes/brief_synthesis.py <trace.json> \
      --probe behavior-proof

Each probe returns a fixed vocabulary answer (PASS/FAIL, GROUNDED/UNGROUNDED,
ALIGNED/MISALIGNED) or a SKIP/NEEDS-LLM note so an unconfigured environment
never hard-fails.
"""

import argparse
import json
import os
import re
from pathlib import Path

# Optional LLM client. Only used when a provider/model is configured via env.
# Leave unset to run the deterministic pre-checks and skip the LLM turn.
LLM_API = os.environ.get("EVAL_LLM_API", "")
LLM_MODEL = os.environ.get("EVAL_LLM_MODEL", "")

# Model the plan routes the semantic turn through in CI (muse-spark tier).
PLAN_LEVEL3_MODEL = "opencode/muse-spark-1.2-contributor-free"

CODE_EXT = (".py", ".ts", ".js", ".go", ".rs", ".md")


def _yes_no(prompt: str) -> str:
    """One binary question to the configured LLM. Returns PASS / FAIL / SKIP."""
    if not LLM_API or not LLM_MODEL:
        return "SKIP"
    # Placeholder transport: kept provider-free so the module stays
    # stdlib-only. Wire your endpoint at call time; CI uses the reusable
    # ai-code-review workflow (muse-spark) instead of this local hook.
    return "SKIP"


def _file_tokens(cmd: str) -> set:
    files = set()
    for token in cmd.replace("/", " ").split():
        if token.endswith(CODE_EXT):
            files.add(token.split("/")[-1])
    return files


def _text(trace: dict) -> str:
    return " ".join(
        [str(trace.get("final_response", ""))]
        + [str(s.get("final_output", "")) for s in trace.get("subagents", [])]
    )


def probe_brief_restraint(trace: dict) -> str:
    """Do dispatched briefs restrict writes to disjoint targets (W4/W6)?"""
    subs = [s for s in trace.get("subagents", []) if s.get("tool_calls")]
    if len(subs) < 2:
        return "SKIP: fewer than two dispatched children to judge"
    seen_targets = []
    for s in subs:
        files = set()
        for tc in s["tool_calls"]:
            cmd = str(
                tc.get("input", {}).get("command")
                or tc.get("input", {}).get("argsSummary")
                or ""
            )
            files |= _file_tokens(cmd)
        seen_targets.append(files)
    overlapping = False
    for i in range(len(seen_targets)):
        for j in range(i + 1, len(seen_targets)):
            if seen_targets[i] & seen_targets[j]:
                overlapping = True
    if not overlapping:
        return "PASS: child tool streams touch disjoint target files"
    if LLM_API and LLM_MODEL:
        return _yes_no(
            "Do the dispatched briefs restrict writes strictly to disjoint targets? "
            "Answer PASS or FAIL with a one-line reason."
        )
    return "NEEDS-LLM: overlapping file tokens found; configure EVAL_LLM_API to judge briefs"


def probe_dismissal_justification(trace: dict) -> str:
    """When a reviewer finding is dismissed, is it backed by repo facts?"""
    text = _text(trace)
    low = text.lower()
    dismissed = "dismiss" in low or "not a bug" in low or "out of scope" in low
    if not dismissed:
        return "SKIP: no dismissal found to judge"
    has_facts = any(
        marker in text
        for marker in ("git show", "HEAD:", "line", "grep", "commit", "test", "assert")
    )
    if has_facts:
        return "GROUNDED: dismissal cites observable repo facts"
    if LLM_API and LLM_MODEL:
        return _yes_no(
            "Is the dismissal backed by an observable repo fact or evidence, or is it "
            "conversational rationalization? Answer GROUNDED or UNGROUNDED."
        )
    return "NEEDS-LLM: dismissal without obvious factual citation; configure EVAL_LLM_API to judge"


def probe_behavior_proof(trace: dict) -> str:
    """Feature acceptance tests must exercise user-observable behavior (W3)."""
    if trace.get("task_type") != "feature":
        return "SKIP: not a feature task"
    diff = trace.get("patch_diff", "")
    if not diff:
        return "SKIP: no patch diff recorded"
    boundary = re.compile(
        r"(subprocess|sys\.argv|exit_code|returncode|stdout|requests?\.|urllib|run\(\[\])"
    )
    mocked_internal = re.compile(r"mock|monkeypatch|patch\(|call_count|assert_called")
    if not boundary.search(diff):
        return "MISALIGNED: feature diff exercises no user-observable boundary"
    if mocked_internal.search(diff) and "subprocess" not in diff:
        return "MISALIGNED: boundary proof relies on mocks, not real output"
    return "ALIGNED: feature diff proves user-observable behavior"


def main():
    parser = argparse.ArgumentParser(description="Level-3 semantic micro-probes.")
    parser.add_argument(
        "trace_json", help="extracted trace JSON (trace_extractor output)"
    )
    parser.add_argument(
        "--probe",
        choices=[
            "brief-restraint",
            "dismissal-justification",
            "behavior-proof",
        ],
        default="brief-restraint",
    )
    args = parser.parse_args()
    trace = json.loads(Path(args.trace_json).read_text(encoding="utf-8"))
    probes = {
        "brief-restraint": probe_brief_restraint,
        "dismissal-justification": probe_dismissal_justification,
        "behavior-proof": probe_behavior_proof,
    }
    print(probes[args.probe](trace))


if __name__ == "__main__":
    main()
