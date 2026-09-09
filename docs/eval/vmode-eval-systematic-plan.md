# Plan: Systematic, Low-LLM Evaluation Harness for Agent Workflows

Date: 2026-09-03
Target: `tests/eval/` in `vstack`
Status: Proposed architecture and implementation roadmap

---

## 1. Problem & Objectives

Current evaluations rely heavily on running full, multi-turn LLM agent sessions and grading transcripts with another LLM. This approach suffers from:
1. **High cost and latency:** Full agent runs take minutes and consume significant token budgets.
2. **Flakiness and non-determinism:** LLM-as-a-judge evaluations fluctuate across runs without reproducible assertions.
3. **Low CI suitability:** Cannot run on every commit or PR.

### Goal
Invert the evaluation pyramid. Implement a systematic test framework where:
- **Level 1 (0% LLM, static checks, <100ms):** Structural linting of skill definitions, markdown contracts, and prompt templates (`static-evals`).
- **Level 2 (0% LLM, deterministic trace evaluation, <1s):** Programmatic verification of execution traces against concrete behavioral contracts W1–W7 (`static-evals`).
- **Level 3 (<20% LLM, targeted semantic probes, cheap & fast):** Isolated single-turn checks targeting only synthesis and reasoning boundaries via Muse Spark (`llm-evals`).

---

## 2. Target Architecture

```
tests/eval/
├── README.md                      # Guide to running, adding, and ingesting traces
├── schema.py                      # Data model for execution traces (Pydantic / dataclasses)
├── trace_extractor.py             # Parser converting raw CLI/subagent logs into schema JSON
├── test_skill_contracts.py        # Level 1: Static checks on skill contracts & markdown
├── test_trace_invariants.py       # Level 2: Deterministic verification of run traces (W1-W7)
├── probes/                        # Level 3: Targeted single-turn micro-evals
│   └── test_brief_synthesis.py    # Isolated single-prompt contract adherence
└── fixtures/                      # Canonical traces for regression testing
    ├── trace_round1_fail.json     # Expected to fail W1, W2, W3, W5, W6
    ├── trace_round2_pass.json     # Expected to pass all contracts
    └── trace_w4_concurrency.json  # Validates true parallel execution window
```

---

## 3. Detailed Component Specifications

### 3.1 Trace Schema (`tests/eval/schema.py`)

A vendor-agnostic trace schema capturing interactions from OpenCode, Pi, or headless harnesses:

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class ToolCall:
    tool: str
    input: Dict[str, Any]
    output: Optional[str] = None
    exit_code: Optional[int] = None
    start_time_ms: Optional[int] = None
    end_time_ms: Optional[int] = None

@dataclass
class SubagentRun:
    subagent_id: str
    role: str
    prompt: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    final_output: str = ""
    start_time_ms: int = 0
    end_time_ms: int = 0

@dataclass
class TaskTrace:
    task_id: str
    task_type: str  # "feature" | "bugfix" | "investigation"
    repository: str
    initial_prompt: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    subagents: List[SubagentRun] = field(default_factory=list)
    patch_diff: str = ""
    final_response: str = ""
```

---

### 3.2 Level 1: Static Skill & Playbook Contracts (`test_skill_contracts.py`)

**Execution Time:** < 100ms | **LLM Usage:** 0%

Deterministic assertions executed directly via `pytest`:
- **Frontmatter integrity:** Ensure every skill in `~/.agents/skills` or repository has valid YAML frontmatter (`name`, `description`).
- **Required skill dependencies:** Assert all skills listed under `Required skills` in `vmode/SKILL.md` exist on disk.
- **Rule compliance linter:**
  - Zero em dashes (`—`) across all markdown playbooks and skill documentation.
  - No narrative comment patterns (`// Phase 1:`, `// Step 2:`) in template references.
- **Role brief templates:** Assert that role templates in `vmode/references/roles.md` contain strict evidence return clauses (`git diff --stat`, test stdout, anchored `grep -n`).

---

### 3.3 Level 2: Deterministic Trace Invariants (`test_trace_invariants.py`)

**Execution Time:** < 500ms | **LLM Usage:** 0%

Transforms the seven evaluation weaknesses into programmatic test functions evaluated against `TaskTrace`:

#### W1: Line Citation Anchoring
- **Invariant:** If `subagent.final_output` cites code locations matching `(\S+\.\w+):(\d+)(?:-(\d+))?`, the trace must contain a prior tool invocation (`grep -n`, `read`, or AST query) on that exact file.
- **Assertion:** Match cited line numbers against the actual tool output recorded in the trace. Off-by-one or fabricated line citations fail immediately.

#### W2 & W7: Functional Skill Manifest Validation
- **Invariant:** Before any task modifications, the parent trace must show a check on skill existence via filesystem tools (`stat`, `access`, `read`, `glob`) or a package manifest lookup.
- **Assertion:** If a required skill is simulated as missing, verify that `set-it-up --required` is triggered before task execution.

#### W3: Outer Boundary Proof
- **Invariant:** For feature tasks, the resulting patch diff (`trace.patch_diff`) must touch an executable acceptance test, CLI runner, or HTTP client boundary, rather than only internal unit functions.
- **Assertion:**
  - Diff contains assertions on `exit_code`, `subprocess.run`, `sys.argv`, or stdout stream.
  - Test runner execution in trace verifies the boundary artifact.

#### W4: True Parallel Execution Window
- **Invariant:** When two or more independent workstreams with disjoint targets are declared, their execution spans must overlap.
- **Formula:**
  $$\text{Overlap} = \max(0, \min(\text{end}_A, \text{end}_B) - \max(\text{start}_A, \text{start}_B))$$
- **Assertion:** `assert overlap > 0`. If execution is serial without documented file collision reasons, the test fails.

#### W5: Headless Local Review Fallback
- **Invariant:** If `hunk-review` fails or returns `skip: no live session`, the trace must contain a fallback review dispatch (`requesting-code-review` or a reviewer subagent).
- **Assertion:** `assert has_reviewer_fallback(trace) == True`.

#### W6: Raw Evidence Attachment
- **Invariant:** Subagent outputs must return verifiable execution evidence, not bare prose claims.
- **Assertion:** Subagent responses must match regex patterns for test execution summaries (e.g. `passed in \d+\.\d+s`, `OK`, `FAIL`), diff stats (`\d+ files? changed`), or line anchors (`\d+:`).

---

### 3.4 Level 3: Targeted Micro-Probes (`probes/test_brief_synthesis.py`)

**Execution Time:** 1–3s | **Model:** `opencode/muse-spark-1.2-contributor-free` (via OpenCode CI runner)

Used exclusively when semantic intent or synthesis quality cannot be proven via static syntax or regex:
1. **Brief Relevance & Boundary Restraint:** Provide the task spec and the parent's generated subagent brief. Probe: *"Does this brief restrict write access strictly to disjoint targets without leaky context? Answer [PASS/FAIL] with reason."*
2. **Reviewer Dismissal Justification:** When an agent dismisses a reviewer finding, probe: *"Is the dismissal backed by an observable repo fact or evidence, or is it conversational rationalization? Answer [GROUNDED/UNGROUNDED]."*
3. **Behavior Proof Alignment:** When reviewing a feature acceptance test, verify that the test exercises user-observable behavior (CLI flags, return codes, output contracts) rather than internal mocked implementation details.

---

## 4. Execution Workflow & CI Integration

### Fast Local / Pre-Commit Loop (0% LLM)
```bash
pytest tests/eval/test_skill_contracts.py
pytest tests/eval/test_trace_invariants.py
```
Runs in `< 1s` locally without network access, credentials, or token expenditure.

### Ingesting New Run Logs
```bash
python3 tests/eval/trace_extractor.py /tmp/vmode-sim/investigate/run.log --output tests/eval/fixtures/latest_run.json
pytest tests/eval/test_trace_invariants.py --trace=tests/eval/fixtures/latest_run.json
```

### GitHub Actions CI Workflow: Level 3 Probes with Muse Spark

Level 3 runs in CI using the existing `vuon9/gh-workflows/.github/workflows/ai-code-review.yml` reusable workflow with `opencode/muse-spark-1.2-contributor-free` (zero added cost, fast contributor-tier inference).

#### Workflow Structure (`.github/workflows/vmode-eval.yml`):

```yaml
name: vmode-eval

on:
  pull_request:
    paths:
      - 'vmode/**'
      - 'tests/eval/**'
      - 'docs/eval/**'
      - '.github/workflows/vmode-eval.yml'

concurrency:
  group: vmode-eval-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

jobs:
  static-evals:
    name: "static-evals (contracts & traces)"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pytest pydantic
      - name: Run Level 1 (static) & Level 2 (trace invariants)
        run: |
          pytest tests/eval/test_skill_contracts.py
          pytest tests/eval/test_trace_invariants.py

  llm-evals:
    name: "llm-evals (muse-spark semantic probes)"
    needs: static-evals
    permissions:
      contents: read
      pull-requests: write
    uses: vuon9/gh-workflows/.github/workflows/ai-code-review.yml@v0.4.1
    with:
      mode: pr
      comment-marker: vmode-llm-eval
      model: opencode/muse-spark-1.2-contributor-free
      prompt: |
        SEMANTIC PROBE EVALUATION: vmode behavioral & contract adherence probe.
        Evaluate PR changes affecting vmode skills, playbooks, or traces.
        Do NOT run shell commands or modify files. Use the read tool only.

        Verify these 3 semantic points:
        1. Role Brief Restraint (W1, W6): Are subagent briefs strictly bounded with
           explicit raw evidence requirements (`git diff --stat`, `grep -n`, test logs)?
        2. Behavior Boundary Fallback (W3): Does feature proof mandate automated
           assertions at the user surface (CLI stdout/exit code, API contract)
           rather than internal functions?
        3. Review Fallback Robustness (W5): Is the fallback gate operational
           when interactive tools (e.g. hunk-review) are absent?

        Post a compact verdict (under 10 lines):
        - Status: PASS or FAIL
        - Semantic Probes: [Brief Restraint: PASS/FAIL, Boundary: PASS/FAIL, Fallback: PASS/FAIL]
        - Notes: concrete reason if failed, or 1-sentence confirmation.
    secrets:
      OPENCODE_API_KEY: ${{ secrets.OPENCODE_API_KEY }}
```

---

## 5. Implementation Roadmap

1. **Step 1:** Create `tests/eval/schema.py` and `tests/eval/trace_extractor.py` to normalize run logs.
2. **Step 2:** Write `tests/eval/test_skill_contracts.py` for static repo/skill linting.
3. **Step 3:** Convert the recorded transcripts from Round 1 and Round 2 into fixture JSON files (`fixtures/trace_round1_fail.json`, `fixtures/trace_round2_pass.json`).
4. **Step 4:** Implement `tests/eval/test_trace_invariants.py` asserting W1–W7 on the fixtures to prove test fidelity.
5. **Step 5:** Document invocation instructions in `tests/eval/README.md`.
