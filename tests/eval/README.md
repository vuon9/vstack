# tests/eval: systematic evaluation harness for agent workflows

Deterministic, low-LLM checks for the vmode skill contracts and the recorded
agent-run traces. Implements the architecture in the (local) plan
`docs/eval/vmode-eval-systematic-plan.md`.

The harness inverts the evaluation pyramid: almost everything here is 0% LLM,
fast, and CI-safe. LLM use is confined to opt-in Level-3 micro-probes that are
never auto-run.

## Levels

### Level 1: static skill & playbook contracts (0% LLM, ~15ms)

`test_skill_contracts.py` checks the repository directly (not ~/.agents, so CI
works on a clean checkout):

- frontmatter integrity (name, "Use when" description, README) for every local skill
- vmode required-skill list matches disk + skills.json (`required: true`)
- no em dashes in vmode playbooks; no narrating-comment patterns in code blocks
- role brief templates contain the evidence clauses (raw evidence, `grep -n`)

### Level 2: deterministic trace invariants (0% LLM, ~10ms)

`invariants.py` turns the W1-W7 evaluation weaknesses into pure functions over
the `TaskTrace` schema. `test_trace_invariants.py` proves fidelity on the
canonical fixtures:

| Fixture | Expected | Why |
| --- | --- | --- |
| `trace_round1_feature.json` | W3 violation | round 1 diff had no user-boundary test |
| `trace_round1_investigate.json` | W1 violation | subagent cited 43 lines, file has 49 |
| `trace_round2_feature.json` | clean | CLI-boundary test added |
| `trace_round2_investigate.json` | clean | citations grep-anchored |
| `trace_w4_concurrency.json` | clean + overlap | two workers, verified overlap |

Fixtures were extracted from the real round-1 / round-2 / W4 runs with
`trace_extractor.py`, so a violation in a fixture is a violation that actually
happened.

### Level 3: semantic micro-probes (opt-in, <20% LLM)

`probes/brief_synthesis.py` covers the two boundaries where regex parsing is
insufficient: brief-disjointness and dismissal-evidence. Each asks one binary
YES/NO question. Deterministic pre-checks run first; the LLM branch is only
reached when `EVAL_LLM_API` and `EVAL_LLM_MODEL` are set. Without them the
probes degrade to YES/SKIP/NEEDS-LLM and never hit the network, so CI stays
0-LLM. `probes/test_brief_synthesis.py` covers only the deterministic paths.

## Running

```bash
# Full suite (Level 1 + 2 + probe deterministic paths), same command as CI
python3 -m unittest discover -s tests

# Just the eval suite
python3 -m unittest tests.eval.test_skill_contracts tests.eval.test_trace_invariants -v

# Verify an arbitrary extracted trace against all W1-W7 invariants
python3 tests/eval/run_invariants.py tests/eval/fixtures/trace_w4_concurrency.json
EVAL_TRACE=tests/eval/fixtures/trace_round1_investigate.json \
  python3 -m unittest tests.eval.run_invariants
```

The existing CI workflow (`.github/workflows/validate.yml`) already runs
`python3 -m unittest discover -s tests`, so Levels 1-2 and the probe
deterministic paths run on every push and PR with zero API cost.

### Level 3 in CI (semantic probes)

`.github/workflows/vmode-eval.yml` gates vmode changes on the full eval stack,
path-limited to `vmode/`, `tests/eval/`, and the workflow itself:

- `static-evals`: Level 1 + Level 2 + probe pre-checks, 0% LLM, gating.
- `llm-evals`: Level 3 semantic probes run after the static gate via the
  `vuon9/gh-workflows` reusable `ai-code-review.yml` with
  `opencode/muse-spark-1.2-contributor-free` (zero-added-cost contributor
  tier). It posts a compact PASS/FAIL verdict under the `vmode-llm-eval`
  marker covering the three probes: brief restraint, behavior boundary,
  review fallback.

Run the probes locally on any extracted trace:

```bash
python3 tests/eval/probes/brief_synthesis.py <trace.json> --probe brief-restraint
python3 tests/eval/probes/brief_synthesis.py <trace.json> --probe dismissal-justification
python3 tests/eval/probes/brief_synthesis.py <trace.json> --probe behavior-proof
```

Set `EVAL_LLM_API` and `EVAL_LLM_MODEL` to enable the LLM branch; without
them the probes return PASS/FAIL/GROUNDED/ALIGNED where deterministically
provable and SKIP/NEEDS-LLM elsewhere, so CI stays 0-LLM.

## Ingesting a new run

`trace_extractor.py` converts pi session transcripts (and optional child
`subagent-artifacts`) into `TaskTrace` JSON:

```bash
python3 tests/eval/trace_extractor.py ~/.pi/agent/sessions/<session>.jsonl \
    --task-type investigation --artifacts-dir <session-dir>/subagent-artifacts \
    --output tests/eval/fixtures/latest_run.json

python3 tests/eval/run_invariants.py tests/eval/fixtures/latest_run.json
```

Source formats understood:

- pi **session transcript** (NDJSON `"type": "session"` records): primary
  source; tool stdout from `toolResult`, timestamps per record.
- pi **child transcripts** under `subagent-artifacts/*.jsonl`
  (`recordType` tool_start/tool_end with epoch-ms `ts`): enrich timing for W4.
- pi **activity run.log** (`"type": "background-task-activity"`): fallback with
  no timestamps; W4 will be skipped on such traces.

Adaptations vs. the plan: stdlib `unittest` instead of pytest (repo constraint:
no external deps); trace selection via CLI args or `EVAL_TRACE` instead of
`pytest --trace=`; per-run fixtures instead of a single aggregate round1_fail
(because no single run trips every weakness). Schema uses dataclasses, not
Pydantic, matching the repo's stdlib-only rule.

## Adding a check or fixture

1. Add a `check_*` function in `invariants.py` and register it in `ALL_CHECKS`.
2. Export the invariant in `run_invariants.py` output automatically (it iterates `ALL_CHECKS`).
3. To prove it fires, add a fixture (or use `run_invariants.py` on a live trace) and a fidelity test in `test_trace_invariants.py`.
4. Keep it deterministic: no network, no clock, no LLM. If you need semantics, use a Level-3 probe instead.
