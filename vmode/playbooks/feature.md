### Feature

**You own the design. Plan, review, verify.** Delegate implementation to subagents or execute in-process; stay in the lead.

Use when building or adding new behavior.

1. **Clarify requirements and design first.**
   Requirements clear? Open `brainstorming` and drive it to a concrete design.
   Scope foggy or spans multiple sessions? Open `wayfinder` and resolve the tickets before coding.
2. **Design before code.**
   When integrating into existing systems or complex subsystems, map the territory before modeling:
   - Trace integration points via `how`: understand existing lifecycle hooks, call chains, and data models before introducing new abstractions.
   - Check constraints via `why`: inspect `git blame` or history on shared boundaries to avoid violating established contracts or repeating discarded patterns.
   Name the data shape and boundary first. Model the domain with clear state structures rather than scattered conditionals.
3. **Throughput checkpoint.**
   Before implementation, write the throughput checkpoint as four items:
   - **Blocking first steps.** Gates and foundation work that must complete before any parallel slices.
   - **Independent workstreams.** Work that can proceed concurrently without overlapping write targets.
   - **Shared mutable state.** Boundaries where concurrent writes would collide. Separate targets first.
   - **Smallest safe decomposition.** The minimal safe chunking for this task.
   If 2+ independent workstreams have strictly disjoint write targets, dispatch them concurrently and reconcile their diffs. If work targets overlap or share mutable state, serialize execution and state the collision reason.
4. **Implementation and delegation.**
   For scoped units, use `test-driven-development`.
   When delegating to a subagent, provide:
   - Clear scope and exact target paths.
   - Named data shape and boundary invariants.
   - Verification command or criteria.
   - Capability role brief (`general` for isolated implementation, `research` for exploratory tracing).
   Require the child to return raw execution evidence (passing test logs, `git diff --stat`). Review the resulting diff yourself; do not pass through subagent claims unverified.
5. **Prove the behavior.**
   For user-facing features, run behavior/feature tests. Prove it against the real artifact, not just "it compiles". Exercise the user-facing boundary (CLI output/exit codes, HTTP response, or public API contract) with automated assertions. If no BDD framework exists, write an executable acceptance test or runner script exercising this outer boundary.
   <!-- EDIT: behavior-test --> Replace this line with your behavior-test command or approach.
6. **Local review.**
   Run `hunk-review` on the local diff before opening a PR. Check adherence to comments and prose rules. If no live Hunk review session is active, run `requesting-code-review` on the local diff or dispatch a fresh reviewer subagent with the diff to audit comments and prose before proceeding.
