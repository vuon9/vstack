# vmode Evaluation Report

Comprehensive record of the vmode evaluation cycle: initial weaknesses, hardening fixes, empirical retest results, and parallel execution verification.

---

## Quick Status Matrix

| ID | Issue | Severity | Root Cause | Fix Applied | Retest Result |
| --- | --- | --- | --- | --- | --- |
| **W1** | Citation drift (off-by-one lines) | High | No operational line-lookup instruction | Mandate `grep -n` verified line citations in `roles.md` | **PASS**: Citations matched `grep -n` exactly |
| **W2** | Name-only skill check | Medium | Prompt catalog trusted without disk check | Mandate filesystem/manifest check in `SKILL.md` | **PASS**: Verified real paths on disk |
| **W3** | Unit test fallback for behavior | Medium | EDIT marker blank; no default fallback | Require user-boundary assertions in `feature.md` | **PASS**: Added automated CLI boundary test |
| **W4** | Serial-only delegation | Medium | No explicit concurrency trigger | Add trigger on disjoint write targets in `feature.md` | **PASS**: 2 children ran concurrently (~43s overlap) |
| **W5** | Hunk review skipped | Medium | Tool requires interactive UI | Fallback to reviewer subagent in playbooks | **PASS**: Dispatched reviewer child |
| **W6** | Parent verification bottleneck | High | Subagents returned prose claims, not proof | Require raw output (`git diff --stat`, test logs) | **PASS**: Parent spot-checked attached proof |
| **W7** | Stale session context | Low | Runtime prompt lagged filesystem | Handled by W2 filesystem check | **PASS**: Verified via disk presence |

---

## 1. Weaknesses & Hardening

### W1: Subagent Citation Drift

- **Defect**: Read-only research subagents hallucinated line offsets (reported 43 lines instead of 49; every symbol offset by one).
- **Fix**: Updated `vmode/references/roles.md` to require anchoring symbols with `grep -n` before reporting.

### W2: Non-Functional Skills Check

- **Defect**: Parent checked names against the session prompt list, meaning broken or missing skills on disk went undetected.
- **Fix**: Updated `vmode/SKILL.md` to check directory existence and non-empty `SKILL.md` files; triggers `set-it-up --required` on failure.

### W3: Behavior-First Default

- **Defect**: Features defaulted to internal unit tests plus ad-hoc manual CLI invocations.
- **Fix**: Updated `vmode/playbooks/feature.md` step 5 to require automated assertions against outer boundaries (CLI exit code/stdout, HTTP payloads, or public API contracts).

### W4: Concurrent Delegation

- **Defect**: Tasks always ran with a single serial child; parallel merge logic was never exercised.
- **Fix**: Updated `vmode/playbooks/feature.md` step 3 to mandate concurrent dispatch when independent workstreams touch disjoint files.

### W5: Headless Review Fallback

- **Defect**: `hunk-review` was skipped in non-interactive headless runs, causing authors to review their own code.
- **Fix**: Added fallback to `requesting-code-review` or a dedicated reviewer subagent in `feature.md` and `bug-fix.md`.

### W6: Parent Verification Bottleneck

- **Defect**: Children returned prose assertions ("tests pass"), forcing parents to re-read all code to verify.
- **Fix**: Brief templates in `roles.md` now mandate raw execution proof (`git diff --stat`, exact test logs, grep output).

---

## 2. Retest Results

Simulated across isolated repos using `deepseek-v4-pro` in headless sessions:

- **Feature Run**: 4/4 tests passed (3 unit + 1 CLI boundary asserting returncode 0 and exact stdout). Delegated review caught a stale docstring.
- **Bug-Fix Run**: One-file minimal diff (-5/+2). Delegated review audited cleanly.
- **Investigate Run**: Citations matched ground truth line-for-line using `grep -n` output.
- **Parallel Dispatch (W4)**: Two workers dispatched 47ms apart on disjoint targets (`src/area.py` and `src/temp.py`) with ~43s concurrent execution overlap. Parent reconciled and verified all 4 tests.
- **Cost**: ~$0.022 to $0.024 per run. Reply discipline held across all runs (no em dashes, consumer named first).

---

## Appendix: W4 re-test procedure

W4 is the one weakness whose verification depends on a specific task shape
(two genuinely disjoint workstreams). Keep this recipe to re-run the check if
vmode's dispatch rules ever change.

### What W4 claims

`feature.md` step 3/4: if 2+ independent workstreams have strictly disjoint
write targets, dispatch them concurrently and reconcile the diffs. If targets
overlap or share mutable state, serialize and state the collision reason.
The serial half is observed and works. The concurrent half (dispatch two
children in parallel, then a parent merge) is what this recipe verifies.

### Task design (one parent, two disjoint files)

Seed a repo with two independent modules that share no mutable state and a
runner that imports both:

```text
src/area.py      (pure functions, area of rectangle)
src/temp.py      (pure functions, C to F conversion)
tests/test_area.py
tests/test_temp.py
```

Prompt (single headless session, vmode mode):

"Work in vmode mode. Add two features: (1) a rectangle perimeter function in
src/area.py with tests, (2) a kelvin-to-celsius conversion in src/temp.py with
tests. The two files and their tests are independent and do not overlap.
Follow vmode's rules: read the feature playbook, run the throughput
checkpoint, and dispatch the two workstreams concurrently if the checkpoint
finds disjoint targets. Verify both test files pass. Name the principles that
shaped your decisions."

### Success criteria

1. Parent runs the feature playbook and the throughput checkpoint.
2. Checkpoint identifies 2 disjoint workstreams (area vs temp).
3. Two children dispatched concurrently (evidence: overlapping/async subagent
   calls or two distinct child results in the transcript).
4. Parent reconciles both diffs itself and does not pass through child claims.
5. Both test files pass on the real artifact.
6. Parent reports the collision reasoning only if it serialized instead.

### Failure modes to watch

- Parent serializes despite disjoint targets (no concurrency attempted).
- Two children write overlapping files (checkpoint missed a shared target).
- Parent merges without re-verifying (accepts child claims).
- One child's change breaks the other's tests (merge conflict missed).

### Known pass (2026-09-02)

Run in /tmp/vmode-sim3/parallel met all criteria: two worker transcripts
started 47ms apart (18:52:51.515Z and 18:52:51.562Z) with ~43s overlapping
windows; each child confined itself to its own files and noted the sibling's
concurrent edits; the parent reconciled one docstring fix and verified 4/4
tests. W4 is EXERCISED. Re-run the same task if dispatch rules change.
