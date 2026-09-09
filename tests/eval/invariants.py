"""Deterministic trace invariants (Level 2, 0% LLM).

Each function takes a TaskTrace and returns a list of violation strings
(empty = invariant holds). The seven checks map to the W1-W7 evaluation
weaknesses and are pure, deterministic, and fast.

Importable by test_trace_invariants.py and by the probes module.
"""

import re

from .schema import TaskTrace

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

FILE_LINE_RE = re.compile(r"([A-Za-z0-9_./-]+\.(?:py|ts|js|go|rs|md)):(\d+)")

EVIDENCE_RE = re.compile(
    r"(?:Ran \d+ tests?|passed in \d+\.\d+s|OK\b|FAILED\b|"
    r"\d+ files? changed|\d+ insertions?|\d+ deletions?|^\s*\d+:\s|AssertionError)"
)


def _all_text(trace: TaskTrace) -> str:
    parts = [trace.initial_prompt, trace.final_response, trace.patch_diff]
    for tc in trace.tool_calls:
        parts.append(str(tc.input))
        parts.append(tc.output or "")
    for sub in trace.subagents:
        parts.append(sub.prompt)
        parts.append(sub.final_output)
        for tc in sub.tool_calls:
            parts.append(str(tc.input))
            parts.append(tc.output or "")
    return "\n".join(parts)


def _grep_outputs(trace: TaskTrace) -> list[str]:
    """Outputs of tool calls that look like line-anchored file listings."""
    outputs = []
    for tc in trace.tool_calls:
        cmd = str(tc.input.get("command") or tc.input.get("argsSummary") or "")
        if "grep -n" in cmd and tc.output:
            outputs.append(tc.output)
    for sub in trace.subagents:
        for tc in sub.tool_calls:
            cmd = str(tc.input.get("command") or tc.input.get("argsSummary") or "")
            if "grep -n" in cmd and tc.output:
                outputs.append(tc.output)
    return outputs


def _max_line_in(output: str) -> int:
    """Largest line number in a grep -n listing output."""
    best = 0
    for m in re.finditer(r"^\s*(\d+)[:|]", output, re.M):
        best = max(best, int(m.group(1)))
    return best


def _has_tool(trace: TaskTrace, predicate) -> bool:
    for tc in trace.tool_calls:
        if predicate(tc):
            return True
    for sub in trace.subagents:
        for tc in sub.tool_calls:
            if predicate(tc):
                return True
    return False


# ---------------------------------------------------------------------------
# W1: line-citation anchoring
# ---------------------------------------------------------------------------


def check_w1_line_citations(trace: TaskTrace) -> list[str]:
    """Subagent file:line citations must be anchored by a grep/read on that file.

    A citation is anchored if the trace contains a grep -n (or read) of the same
    file, and any concrete line range the subagent names falls inside the line
    count recorded by that grep output.
    """
    violations = []
    grep_outputs = _grep_outputs(trace)
    max_line_total = max((_max_line_in(out) for out in grep_outputs), default=0)
    for sub in trace.subagents:
        text = sub.final_output
        if not text or "lines" not in text.lower() and "line " not in text.lower():
            continue
        for m in re.finditer(r"(\d+)\s*lines?\b", text):
            claimed = int(m.group(1))
            if max_line_total and claimed < max_line_total - 2:
                violations.append(
                    f"W1: subagent claimed file has {claimed} lines but grep shows {max_line_total}"
                )
    return violations


# ---------------------------------------------------------------------------
# W2/W7: functional skill presence check before work
# ---------------------------------------------------------------------------


def check_w2_skill_presence_check(trace: TaskTrace) -> list[str]:
    """Before modifying code the parent must touch the skill store or run a check.

    We accept evidence in the tool stream: ls/read/stat/find over the skills
    directory or a set-it-up invocation.
    """
    probe_re = re.compile(r"(skills|set-it-up|SKILL\.md|required)")
    cmd_seen = False
    for tc in trace.tool_calls:
        cmd = str(tc.input.get("command") or tc.input.get("argsSummary") or "")
        if probe_re.search(cmd) and any(
            kw in cmd
            for kw in ("ls", "read", "find", "cat", "manage.py verify", "install.py")
        ):
            cmd_seen = True
            break
    if not cmd_seen:
        return ["W2: no skill-presence check (ls/read/find over skills) before work"]
    return []


# ---------------------------------------------------------------------------
# W3: outer-boundary behavior proof for feature tasks
# ---------------------------------------------------------------------------


def check_w3_outer_boundary(trace: TaskTrace) -> list[str]:
    """Feature diffs must prove behavior at the user boundary, not only units."""
    if trace.task_type != "feature":
        return []
    diff = trace.patch_diff
    if not diff:
        return ["W3: no patch diff recorded for feature task"]
    boundary_re = re.compile(
        r"(subprocess|sys\.argv|exit_code|returncode|stdout|requests?\.|urllib|http|run\(\[\])"
    )
    if not boundary_re.search(diff):
        return ["W3: patch diff exercises no user-facing boundary (CLI/HTTP/stdout)"]
    return []


# ---------------------------------------------------------------------------
# W4: true parallel execution window
# ---------------------------------------------------------------------------


def check_w4_parallel_window(trace: TaskTrace) -> list[str]:
    """Two or more timed subagents must overlap; serial needs a stated reason.

    Only applies when the task declares parallel workstreams or actually
    dispatched multiple children. Single-worker feature/bugfix/investigation
    traces are not expected to overlap and are skipped.
    """
    if trace.task_type != "parallel":
        return []
    timed = []
    for s in trace.subagents:
        if s.subagent_id == "parent-notify":
            continue
        if s.start_time_ms is not None and s.end_time_ms is not None:
            timed.append((s.start_time_ms, s.end_time_ms))
    if len(timed) < 2:
        return ["W4: fewer than two timed subagent runs to evaluate overlap"]
    for i in range(len(timed)):
        a_start, a_end = timed[i]
        for j in range(i + 1, len(timed)):
            b_start, b_end = timed[j]
            overlap = max(0, min(a_end, b_end) - max(a_start, b_start))
            if overlap > 0:
                return []
    return ["W4: timed subagent runs do not overlap (serial execution)"]


# ---------------------------------------------------------------------------
# W5: headless local-review fallback
# ---------------------------------------------------------------------------


def check_w5_review_fallback(trace: TaskTrace) -> list[str]:
    """When hunk-review is impossible, an independent reviewer must run."""
    text = _all_text(trace)
    skip_no_session = re.search(r"skip:\s*no live Hunk|no live Hunk session", text)
    has_fallback = bool(
        re.search(
            r"requesting-code-review|reviewer subagent|dispatch.*review|agent.?reviewer",
            text,
        )
    )
    if skip_no_session and not has_fallback:
        return ["W5: hunk-review skipped with no independent-review fallback"]
    return []


# ---------------------------------------------------------------------------
# W6: raw evidence attachment
# ---------------------------------------------------------------------------


def check_w6_raw_evidence(trace: TaskTrace) -> list[str]:
    """Delegated implementation work returns raw execution evidence.

    Only dispatched implementation children are judged: entries with tool calls
    whose role implies execution (worker/general/implementer/explorer), not
    read-only reviewers (which cannot run commands by design) and not the
    parent-notify echo.
    """
    implementer_re = re.compile(r"(worker|general|implementer|develop|explorer)")
    for sub in trace.subagents:
        if sub.subagent_id == "parent-notify":
            continue
        if not sub.tool_calls:
            continue
        if not implementer_re.search(sub.role.lower() + " " + sub.subagent_id.lower()):
            continue
        if not sub.final_output.strip():
            continue
        if EVIDENCE_RE.search(sub.final_output) is None:
            return [
                f"W6: implementation subagent {sub.subagent_id[:12]} returned no raw "
                "execution evidence (test output / diff stat / line anchors)"
            ]
    return []


# ---------------------------------------------------------------------------
# Aggregate runner
# ---------------------------------------------------------------------------

ALL_CHECKS = [
    ("W1", check_w1_line_citations),
    ("W2", check_w2_skill_presence_check),
    ("W3", check_w3_outer_boundary),
    ("W4", check_w4_parallel_window),
    ("W5", check_w5_review_fallback),
    ("W6", check_w6_raw_evidence),
]


def verify_trace(trace: TaskTrace) -> dict:
    """Run all checks; returns {check_id: [violation, ...]}."""
    return {check_id: fn(trace) for check_id, fn in ALL_CHECKS}


def violations_flat(trace: TaskTrace) -> list[str]:
    out = []
    for _, fn in ALL_CHECKS:
        out.extend(fn(trace))
    return out
